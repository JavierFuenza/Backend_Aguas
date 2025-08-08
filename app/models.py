from sqlalchemy import Column, Integer, Date, String, Float, BigInteger, Boolean, DateTime, Identity, Index, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
# Importa Base desde el archivo database.py
from .database import Base

class ObrasMedicion(Base):
    __tablename__ = 'obras_medicion'

    id = Column(Integer, Identity(), primary_key=True, index=True)

    id_med_obr = Column(BigInteger, name='ID.MED.OBR', nullable=True)
    id_informante = Column(BigInteger, nullable=True)
    id_junta = Column(BigInteger, nullable=True)
    region = Column(Integer, index=True, nullable=True) # Added index
    provincia = Column(Integer, nullable=True)
    comuna = Column(Integer, index=True, nullable=True) # Added index
    utm_norte = Column(BigInteger, nullable=True) # Index handled by __table_args__
    utm_este = Column(BigInteger, nullable=True) # Index handled by __table_args__
    huso = Column(Integer, nullable=True)
    codigo = Column(String(255), nullable=True)
    naturaleza = Column(Integer, nullable=True)
    cod_cuenca = Column(Integer, index=True, nullable=True) # Added index
    nom_cuenca = Column(String(255), index=True, nullable=True) # Added index
    cod_acuifero = Column(Integer, nullable=True)
    nom_acuifero = Column(String(255), nullable=True)
    sector_sha = Column(String(255), nullable=True)
    cod_subcuenca = Column(Integer, index=True, nullable=True) # Added index
    nom_subcuenca = Column(String(255), index=True, nullable=True) # Added index
    cod_subsubcuenca = Column(Integer, nullable=True)
    nom_subsubcuenca = Column(String(255), nullable=True)
    cod_fuente_superficial = Column(Integer, nullable=True)
    nom_fuente_superficial = Column(String(255), nullable=True)
    nombre_fuente = Column(String(255), nullable=True)
    extrae_canal = Column(Boolean, nullable=True)
    nombre_canal = Column(String(255), nullable=True)
    apr = Column(Boolean, nullable=True)
    puntoalt = Column(Boolean, nullable=True)
    tiene_motobomba = Column(Boolean, nullable=True)
    tiene_bocatoma = Column(Boolean, nullable=True)
    tipo_bocatoma = Column(String(255), nullable=True)
    descarga_cauce_natural = Column(Boolean, nullable=True)
    habilitada = Column(Boolean, nullable=True)
    motivo_deshabilitada = Column(Integer, nullable=True)
    motivo_otra = Column(String(255), nullable=True)
    estado_obra = Column(Integer, nullable=True)
    motivo_cambio_estado = Column(String(255), nullable=True)
    fecha_cambio_estado = Column(DateTime, nullable=True)
    motivo_cambio_informante = Column(String(255), nullable=True)
    nombre_obra = Column(String(255), index=True, nullable=True) # Added index
    tipo_obra = Column(Integer, nullable=True)
    cod_sector_sha = Column(Integer, nullable=True)
    representa_junta = Column(Boolean, nullable=True)
    parte_junta = Column(Boolean, nullable=True)
    rut_inf = Column(String(12), name='RUT.INF.', nullable=True)
    tip_inf = Column(Integer, name='TIP.INF.', nullable=True)
    nomb_inf = Column(String(255), name='NOMB.INF.', index=True, nullable=True) # Added index
    a_pat_inf = Column(String(255), name='A.PAT.INF.', nullable=True)
    a_mat_inf = Column(String(255), name='A.MAT.INF.', nullable=True)
    nacionalidad = Column(Integer, nullable=True)
    gen_inf = Column(Integer, name='GEN.INF', nullable=True)
    reg_inf = Column(Integer, name='REG.INF.', nullable=True)
    prov_inf = Column(Integer, name='PROV.INF.', nullable=True)
    com_inf = Column(Integer, name='COM.INF.', nullable=True)
    dir_inf = Column(String(255), name='DIR.INF', nullable=True)
    tel_fij_inf = Column(String(50), name='TEL.FIJ.INF.', nullable=True)
    tel_mov_inf = Column(String(50), name='TEL.MOV.INF', nullable=True)
    email_inf = Column(String(255), name='EMAIL.INF', nullable=True)
    rut_usu = Column(String(12), name='RUT.USU.', nullable=True)
    tip_usu = Column(Integer, name='TIP.USU.', nullable=True)
    nomb_usu = Column(String(255), name='NOMB.USU.', nullable=True)
    a_pat_usu = Column(String(255), name='A.PAT.USU.', nullable=True)
    a_mat_usu = Column(String(255), name='A.MAT.USU.', nullable=True)
    reg_usu = Column(Integer, name='REG.USU.', nullable=True)
    pro_usu = Column(Integer, name='PRO.USU.', nullable=True)
    com_usu = Column(Integer, nullable=True)
    gen_usu = Column(Integer, nullable=True)
    dir_usu = Column(String(255), nullable=True)
    tel_fij_usu = Column(String(50), nullable=True)
    tel_mov_usu = Column(String(50), nullable=True)
    email_usu = Column(String(255), nullable=True)
    id_med = Column(BigInteger, nullable=True)
    id_obra_captacion = Column(BigInteger, nullable=True)
    canal_transmision = Column(Integer, nullable=True)
    tipo_medicion = Column(Integer, nullable=True)
    fecha_medicion = Column(DateTime, index=True, nullable=True) # Added index
    fecha_origen = Column(DateTime, nullable=True)
    caudal = Column(Float, index=True, nullable=True) # Added index
    altura_limnimetrica = Column(Float, nullable=True)
    totalizador = Column(Float, nullable=True)
    nivel_freatico = Column(Float, nullable=True)
    rut_empresa = Column(String(12), nullable=True)

    __table_args__ = (
        # Composite index for UTM coordinates, crucial for spatial queries
        Index('idx_utm_coords', 'utm_norte', 'utm_este'),
        # Composite index for filtering by cuenca and subcuenca
        Index('idx_cuenca_subcuenca', 'cod_cuenca', 'cod_subcuenca'),
        # Composite index for time series queries on cuenca and date
        Index('idx_cuenca_fecha_medicion', 'cod_cuenca', 'fecha_medicion'),
        Index('idx_nom_cuenca_fecha_medicion', 'nom_cuenca', 'fecha_medicion'),
    )

class DimUbicacion(Base):
    __tablename__ = 'dim_ubicacion'
    id_ubicacion = Column(Integer, Identity(), primary_key=True, index=True)

    # Campos de la jerarquía geográfica consolidada
    region = Column(Integer)
    provincia = Column(Integer)
    comuna = Column(Integer)
    cod_cuenca = Column(Integer)
    nom_cuenca = Column(String(50))
    cod_subcuenca = Column(String(20))
    nom_subcuenca = Column(String(50))
    cod_subsubcuenca = Column(String(20))
    nom_subsubcuenca = Column(String(50))

    # Clave foránea a DimAcuifero
    id_acuifero = Column(Integer, ForeignKey('dim_acuifero.id_acuifero'))
    
    # Campos originales de ubicación
    utm_norte = Column(BigInteger, index=True)
    utm_este = Column(BigInteger, index=True)
    huso = Column(Integer)
    nombre_fuente = Column(String(100))
    cod_fuente_superficial = Column(String(20))
    
    # Relaciones
    acuifero = relationship("DimAcuifero", back_populates="ubicaciones")
    caudales = relationship("FactCaudales", back_populates="ubicacion")

    __table_args__ = (
        # Constraint de unicidad para ubicaciones (requerido para ETL)
        UniqueConstraint('utm_norte', 'utm_este', 'huso', 'id_acuifero', 
                        name='uq_dim_ubicacion_coords_acuifero'),
    )

class DimAcuifero(Base):
    __tablename__ = 'dim_acuifero'
    id_acuifero = Column(Integer, Identity(), primary_key=True, index=True)
    cod_acuifero = Column(String(20), unique=True, index=True)  # UNIQUE constraint añadido para ETL
    nom_acuifero = Column(String(100), index=True)
    
    # Relación uno a muchos con DimUbicacion
    ubicaciones = relationship("DimUbicacion", back_populates="acuifero")

class DimTiempo(Base):
    __tablename__ = 'dim_tiempo'
    id_tiempo = Column(Integer, Identity(), primary_key=True, index=True)
    fecha_completa = Column(Date, unique=True, index=True)
    dia = Column(Integer)
    mes = Column(Integer)
    ano = Column(Integer)
    
    # Relación uno a muchos con FactCaudales
    caudales = relationship("FactCaudales", back_populates="tiempo")

class DimInformante(Base):
    __tablename__ = 'dim_informante'
    id_informante = Column(Integer, Identity(), primary_key=True, index=True)
    rut_informante = Column(String(12), unique=True)  # Ya tenía UNIQUE
    tipo_informante = Column(String(50))
    nombre_informante = Column(String(100), index=True)
    nacionalidad_informante = Column(String(50))
    genero_informante = Column(String(20))
    
    # Relación uno a muchos con DimObra
    obras = relationship("DimObra", back_populates="informante")

class DimTipoObra(Base):
    __tablename__ = 'dim_tipo_obra'
    id_tipo_obra = Column(Integer, Identity(), primary_key=True, index=True)
    descripcion = Column(String(50), unique=True)  # Ya tenía UNIQUE
    
    # Relación uno a muchos con DimObra
    obras = relationship("DimObra", back_populates="tipo_obra")

class DimEstadoObra(Base):
    __tablename__ = 'dim_estado_obra'
    id_estado_obra = Column(Integer, Identity(), primary_key=True, index=True)
    descripcion = Column(String(50), unique=True)  # Ya tenía UNIQUE
    
    # Relación uno a muchos con DimObra
    obras = relationship("DimObra", back_populates="estado_obra")

class DimObra(Base):
    __tablename__ = 'dim_obra'
    id_obra = Column(Integer, Identity(), primary_key=True, index=True)
    id_med_obr = Column(BigInteger, unique=True)  # Ya tenía UNIQUE
    nombre_obra = Column(String(100), index=True)
    extrae_canal = Column(String(2))
    apr = Column(String(2))
    puntoalt = Column(String(2))
    tiene_motobomba = Column(String(2))
    tiene_bocatoma = Column(String(2))
    descarga_cauce_natural = Column(String(2))
    habilitada = Column(String(2))
    motivo_deshabilitada = Column(String(100))
    motivo_otra = Column(String(100))
    motivo_cambio_estado = Column(String(100))
    fecha_cambio_estado = Column(DateTime)
    
    # Claves foráneas
    id_informante = Column(Integer, ForeignKey('dim_informante.id_informante'))
    id_tipo_obra = Column(Integer, ForeignKey('dim_tipo_obra.id_tipo_obra'))
    id_estado_obra = Column(Integer, ForeignKey('dim_estado_obra.id_estado_obra'))
    
    # Relaciones
    informante = relationship("DimInformante", back_populates="obras")
    tipo_obra = relationship("DimTipoObra", back_populates="obras")
    estado_obra = relationship("DimEstadoObra", back_populates="obras")
    caudales = relationship("FactCaudales", back_populates="obra")

class FactCaudales(Base):
    __tablename__ = 'fact_caudales'
    id = Column(Integer, Identity(), primary_key=True, index=True)
    caudal_m3s = Column(Float)
    
    # Claves foráneas a las tablas de dimensión
    id_ubicacion = Column(Integer, ForeignKey('dim_ubicacion.id_ubicacion'))
    id_tiempo = Column(Integer, ForeignKey('dim_tiempo.id_tiempo'))
    id_obra = Column(Integer, ForeignKey('dim_obra.id_obra'))
    
    # Relaciones
    ubicacion = relationship("DimUbicacion", back_populates="caudales")
    tiempo = relationship("DimTiempo", back_populates="caudales")
    obra = relationship("DimObra", back_populates="caudales")

    __table_args__ = (
        # Índice compuesto para optimizar consultas de hechos
        Index('idx_fact_caudales_composite', 'id_ubicacion', 'id_tiempo', 'id_obra'),
        # Constraint opcional para evitar duplicados exactos en FactCaudales
        UniqueConstraint('id_ubicacion', 'id_tiempo', 'id_obra', 
                        name='uq_fact_caudales_unique_measurement'),
    )