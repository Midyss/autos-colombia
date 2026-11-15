# Parqueadero Autos Colombia

Sistema de información para la gestión de entradas y salidas de vehículos en el parqueadero "Autos Colombia".

## Descripción

Aplicación web desarrollada con Flask y MySQL para administrar un parqueadero de vehículos. Permite registrar entradas y salidas, asignar celdas automáticamente, gestionar usuarios con diferentes roles y consultar el estado del parqueadero en tiempo real.

## Iteración 2 - Plan de Pruebas

Se ejecutaron 10 casos de prueba para validar las funcionalidades del sistema:

| Caso | Descripción | Responsable | Estado |
|------|-------------|-------------|--------|
| PT-01 | Registro de entrada de vehículo | Miledis Suarez | Exitoso |
| PT-02 | Validación de placa duplicada | Diego Ruiz | Exitoso |
| PT-03 | Asignación automática de celda | Daniela Zapata | Exitoso |
| PT-04 | Consulta de vehículos presentes | Miledis Suarez | Exitoso |
| PT-05 | Registro de salida de vehículo | Diego Ruiz | Exitoso |
| PT-06 | Validación de celda disponible | Daniela Zapata | Exitoso |
| PT-07 | Creación de usuario y encriptación | Miledis Suarez | Exitoso |
| PT-08 | Desactivación de usuario | Diego Ruiz | Exitoso |
| PT-09 | Restricción en celda mantenimiento | Daniela Zapata | Exitoso |
| PT-10 | Entrada exitosa en celda disponible | Miledis Suarez | Exitoso |

Las evidencias (capturas de pantalla y consultas SQL) se encuentran en la carpeta `evidencias/`.


## Tecnologías

- Python 3.12 con Flask
- MySQL 8.x
- HTML, CSS y JavaScript
- SQLAlchemy como ORM

## Requisitos

- Python 3.12 instalado
- MySQL Server corriendo
- Base de datos `autos_colombia` creada

## Cómo ejecutar

1. Clonar el repositorio:

https://github.com/Midyss/autos-colombia.git

2. Instalar dependencias:
 pip install -r requirements.txt


3. Configurar la base de datos editando `app/config.py` con las credenciales de MySQL.

4. Ejecutar el proyecto:
 python run.py

5. Acceder desde el navegador en `http://localhost:5000`

## Estudiantes 

- Miledis Suarez
- Diego Ruiz
- Daniela Zapata

Noviembre 2026




