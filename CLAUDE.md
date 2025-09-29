# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) al trabajar con código en este repositorio.

## Comandos Esenciales

### Desarrollo
```bash
# Iniciar todos los servicios (PostgreSQL + FastAPI + pgAdmin)
docker compose up --build

# Detener servicios
docker compose down

# Detener servicios y eliminar volúmenes
docker compose down -v

# Reiniciar servicios (después de Ctrl+C)
docker compose restart
docker compose logs --follow
```

### Puntos de Acceso
- Servidor FastAPI: http://localhost:8000
- Documentación de la API: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (credenciales en archivo .env)
- PostgreSQL: localhost:5432 (postgres/postgres)

## Visión General de la Arquitectura

Este es un sistema de gestión de aguas basado en FastAPI para el seguimiento de mediciones de extracción de agua (obras de medición) en Chile. El sistema maneja datos hidrológicos incluyendo caudales, niveles de agua y coordenadas geográficas.

### Componentes Principales

- **Aplicación FastAPI** (`app/main.py`): Servidor API principal con endpoints completos para análisis de datos hídricos
- **Modelos SQLAlchemy** (`app/models.py`): Modelo principal único `ObrasMedicion` con indexación extensiva para rendimiento
- **Capa de Base de Datos** (`app/database.py`): Conexión PostgreSQL usando SQLAlchemy
- **Configuración Docker**: Configuración multi-contenedor con PostgreSQL, FastAPI y pgAdmin

### Modelo de Datos Clave

El modelo `ObrasMedicion` representa mediciones de extracción de agua con:
- Datos geográficos: coordenadas UTM (utm_norte, utm_este), regiones, cuencas
- Datos de medición: caudales, niveles de agua (altura_limnimetrica, nivel_freatico)
- Datos temporales: fechas de medición (fecha_medicion)
- Datos administrativos: informantes, permisos, detalles de infraestructura

### Estructura de Endpoints de la API

1. **Endpoints de conteo**: Conteo básico de registros
2. **Endpoints de puntos** (`/puntos`): Consultas basadas en coordenadas geográficas con filtrado
3. **Endpoints de cuencas** (`/cuencas`): Análisis y estadísticas basadas en cuencas
4. **Endpoints de series temporales**: Análisis temporal de datos de caudal

### Consideraciones de Rendimiento

El modelo incluye índices estratégicos:
- Índice compuesto de coordenadas UTM para consultas espaciales
- Índices de cuenca y fecha para análisis de series temporales
- Índices individuales en campos consultados frecuentemente (region, caudal, etc.)

### Importación de Datos

Los archivos CSV deben colocarse en el directorio `./data/` e importarse vía pgAdmin usando el comando COPY proporcionado en readme.md.

## Conexión a Base de Datos

Detalles de conexión PostgreSQL:
- Host: db (al usar Docker) / localhost (acceso externo)
- Puerto: 5432
- Base de datos: postgres
- Usuario: postgres
- Contraseña: postgres

Las variables de entorno se definen en el archivo `.env` (no rastreado en git).