from sqlalchemy import func, insert, Column, Integer, String, Float, BigInteger, Boolean, DateTime, Sequence
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
import pandas as pd
import io
import logging

# Importar componentes de la base de datos desde database.py
from .database import SessionLocal, engine, Base
# Importar la función para crear tablas desde db_utils.py
from .db_utils import create_tables
# Importar el modelo ObrasMedicion desde models.py
from .models import ObrasMedicion

app = FastAPI()

@app.on_event("startup")
def on_startup():
    """
    Función que se ejecuta al inicio de la aplicación FastAPI.
    Aquí crearemos todas las tablas definidas en nuestros modelos.
    """
    logging.info("Iniciando la aplicación y creando tablas en la base de datos...")
    create_tables()
    logging.info("Tablas creadas exitosamente o ya existentes.")


@app.get("/obras/count", summary="Obtiene el número total de registros en la tabla ObrasMedicion")
async def get_obras_count():
    db = SessionLocal()
    try:
        count = db.query(func.count(ObrasMedicion.id)).scalar()
        return {"total_records": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/ubicaciones", summary="Obtiene todas las regiones, cuencas y subcuencas con sus códigos y nombres")
async def get_ubicaciones():
    db = SessionLocal()
    try:
        results = db.query(
            ObrasMedicion.region,
            ObrasMedicion.nom_cuenca,
            ObrasMedicion.cod_cuenca,
            ObrasMedicion.nom_subcuenca,
            ObrasMedicion.cod_subcuenca
        ).distinct().all()

        ubicaciones = []
        for r in results:
            ubicaciones.append({
                "cod_region": r.region,
                "nom_cuenca": r.nom_cuenca,
                "cod_cuenca": r.cod_cuenca,
                "nom_subcuenca": r.nom_subcuenca,
                "cod_subcuenca": r.cod_subcuenca
            })
        return ubicaciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/coordenadas_unicas", summary="Obtiene coordenadas únicas filtradas con datos importantes")
async def get_coordenadas_unicas(
    region: Optional[int] = Query(None, description="Filtrar por código de Región"),
    cod_cuenca: Optional[int] = Query(None, description="Filtrar por código de cuenca"),
    cod_subcuenca: Optional[int] = Query(None, description="Filtrar por código de subcuenca"),
    limit: Optional[int] = Query(120, description="Cantidad máxima de coordenadas únicas a retornar")
):
    db = SessionLocal()
    try:
        query = db.query(
            ObrasMedicion.nom_cuenca,
            ObrasMedicion.nom_subcuenca,
            ObrasMedicion.comuna,
            ObrasMedicion.utm_norte,
            ObrasMedicion.utm_este,
            ObrasMedicion.huso # Asumiendo que 'huso' se necesita para "coordenadas normales" o transformación
        ).distinct(
            ObrasMedicion.utm_norte,
            ObrasMedicion.utm_este
        )

        if region is not None:
            query = query.filter(ObrasMedicion.region == region)
        if cod_cuenca is not None:
            query = query.filter(ObrasMedicion.cod_cuenca == cod_cuenca)
        if cod_subcuenca is not None:
            query = query.filter(ObrasMedicion.cod_subcuenca == cod_subcuenca)

        # Limitar la cantidad de resultados únicos
        results = query.limit(limit).all()

        coordenadas = []
        for r in results:
            coordenadas.append({
                "nombre_cuenca": r.nom_cuenca,
                "nombre_subcuenca": r.nom_subcuenca,
                "comuna": r.comuna,
                "utm_norte": r.utm_norte,
                "utm_este": r.utm_este,
                "huso_utm": r.huso,
                # Aquí podrías añadir una lógica para "coordenadas normales" si se refiere a lat/lon
                # Por ahora, se devuelven las UTM.
            })
        return coordenadas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/analisis_cuenca", summary="Realiza un análisis estadístico de caudal por cuenca")
async def get_analisis_cuenca(
    cuenca_identificador: str = Query(..., description="Código o nombre de la cuenca")
):
    db = SessionLocal()
    try:
        query = db.query(ObrasMedicion.caudal)

        if cuenca_identificador.isdigit():  # Si es un número, asumir que es un código
            query = query.filter(ObrasMedicion.cod_cuenca == int(cuenca_identificador))
        else:  # Si no, asumir que es un nombre
            query = query.filter(ObrasMedicion.nom_cuenca == cuenca_identificador)

        # Filtrar registros donde el caudal no es nulo para los cálculos
        query = query.filter(ObrasMedicion.caudal.isnot(None))

        # Calcular estadísticas
        count = query.count()
        avg_caudal = query.with_entities(func.avg(ObrasMedicion.caudal)).scalar()
        min_caudal = query.with_entities(func.min(ObrasMedicion.caudal)).scalar()
        max_caudal = query.with_entities(func.max(ObrasMedicion.caudal)).scalar()
        std_caudal = query.with_entities(func.stddev(ObrasMedicion.caudal)).scalar()

        if count == 0:
            return {"message": "No se encontraron datos de caudal para la cuenca especificada."}

        return {
            "cuenca_identificador": cuenca_identificador,
            "total_registros_con_caudal": count,
            "caudal_promedio": avg_caudal,
            "caudal_minimo": min_caudal,
            "caudal_maximo": max_caudal,
            "desviacion_estandar_caudal": std_caudal
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/informantes_por_cuenca", summary="Genera datos para gráficos de barras de informantes por cuenca")
async def get_informantes_por_cuenca(
    cuenca_identificador: str = Query(..., description="Código o nombre de la cuenca")
):
    db = SessionLocal()
    try:
        base_query = db.query(ObrasMedicion)

        if cuenca_identificador.isdigit():
            base_query = base_query.filter(ObrasMedicion.cod_cuenca == int(cuenca_identificador))
        else:
            base_query = base_query.filter(ObrasMedicion.nom_cuenca == cuenca_identificador)

        # Agrupación por informante para el conteo de registros
        informantes_count = base_query.with_entities(
            ObrasMedicion.nomb_inf,
            func.count(ObrasMedicion.id)
        ).group_by(ObrasMedicion.nomb_inf).all()

        # Agrupación por informante para la suma de caudal total extraído
        informantes_caudal_total = base_query.with_entities(
            ObrasMedicion.nomb_inf,
            func.sum(ObrasMedicion.caudal)
        ).filter(ObrasMedicion.caudal.isnot(None)).group_by(ObrasMedicion.nomb_inf).all()

        # Formatear resultados para el gráfico de cantidad de registros
        data_registros = []
        for nom_inf, count in informantes_count:
            data_registros.append({
                "informante": nom_inf if nom_inf else "Desconocido",
                "cantidad_registros": count
            })

        # Formatear resultados para el gráfico de caudal total
        data_caudal = []
        for nom_inf, total_caudal in informantes_caudal_total:
            data_caudal.append({
                "informante": nom_inf if nom_inf else "Desconocido",
                "caudal_total_extraido": total_caudal if total_caudal else 0
            })
        
        # Opcional: Contar obras únicas por informante
        informantes_obras_unicas = base_query.with_entities(
            ObrasMedicion.nomb_inf,
            func.count(ObrasMedicion.nombre_obra.distinct())
        ).group_by(ObrasMedicion.nomb_inf).all()

        data_obras_unicas = []
        for nom_inf, unique_works_count in informantes_obras_unicas:
            data_obras_unicas.append({
                "informante": nom_inf if nom_inf else "Desconocido",
                "cantidad_obras_unicas": unique_works_count
            })

        return {
            "cuenca_identificador": cuenca_identificador,
            "grafico_cantidad_registros_por_informante": data_registros,
            "grafico_caudal_total_por_informante": data_caudal,
            "grafico_cantidad_obras_unicas_por_informante": data_obras_unicas # Nuevo dato para el gráfico
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/caudal_por_tiempo_por_cuenca", summary="Obtiene el caudal extraído a lo largo del tiempo para una cuenca específica")
async def get_caudal_por_tiempo_por_cuenca(
    cuenca_identificador: str = Query(..., description="Código o nombre de la cuenca"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD) para filtrar mediciones"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD) para filtrar mediciones")
):
    db = SessionLocal()
    try:
        query = db.query(
            ObrasMedicion.fecha_medicion,
            ObrasMedicion.caudal
        )

        if cuenca_identificador.isdigit():
            query = query.filter(ObrasMedicion.cod_cuenca == int(cuenca_identificador))
        else:
            query = query.filter(ObrasMedicion.nom_cuenca == cuenca_identificador)

        # Filtrar solo registros con caudal y fecha de medición no nulos
        query = query.filter(
            ObrasMedicion.caudal.isnot(None),
            ObrasMedicion.fecha_medicion.isnot(None)
        )

        if fecha_inicio:
            query = query.filter(ObrasMedicion.fecha_medicion >= fecha_inicio)
        if fecha_fin:
            query = query.filter(ObrasMedicion.fecha_medicion <= fecha_fin)

        # Ordenar por fecha para una mejor visualización temporal
        query = query.order_by(ObrasMedicion.fecha_medicion)

        results = query.all()

        caudal_por_tiempo = []
        for fecha, caudal in results:
            caudal_por_tiempo.append({
                "fecha_medicion": fecha.isoformat() if fecha else None, # Formato ISO para fechas
                "caudal": caudal
            })
        
        if not caudal_por_tiempo:
            raise HTTPException(status_code=404, detail="No se encontraron datos de caudal para el período o cuenca especificada.")

        return {
            "cuenca_identificador": cuenca_identificador,
            "caudal_por_tiempo": caudal_por_tiempo
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()