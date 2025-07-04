import io
import pandas as pd
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy import func, insert, Column, Integer, String, Float, BigInteger, Boolean, DateTime, Sequence
from sqlalchemy.exc import SQLAlchemyError
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

