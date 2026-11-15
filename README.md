# Parqueadero Autos Colombia - Sistema de Gestión

Sistema de información para la gestión de entradas y salidas de vehículos en el parqueadero "Autos Colombia", el cual opera por mensualidad.

##  Descripción

Aplicación web desarrollada con **Flask (Python)** y **MySQL** para administrar un parqueadero de vehículos con las siguientes funcionalidades:

-  Registro de entrada y salida de vehículos
-  Asignación automática de celdas (Automóvil/Moto)
-  Gestión de usuarios con roles (Administrador/Operador)
-  Encriptación de contraseñas con scrypt
-  Control de estados de celdas (Disponible, Ocupada, Mantenimiento, Inhabilitada)
-  Validaciones de reglas de negocio
-  Trazabilidad de operaciones

---

##  Plan de Pruebas - Iteración 2

Se ejecutaron **10 casos de prueba** validando todas las funcionalidades del sistema:

| Caso | Descripción | Responsable | Estado |
|------|-------------|-------------|--------|
| PT-01 | Registro de entrada de vehículo | Miledis Suarez  |  Exitoso |
| PT-02 | Validación de placa duplicada | Diego Ruiz  |  Exitoso |
| PT-03 | Asignación automática de celda | Daniela Zapata  |  Exitoso |
| PT-04 | Consulta de vehículos presentes | Milediss suarez  |  Exitoso |
| PT-05 | Registro de salida de vehículo | Diego Rui |  Exitoso |
| PT-06 | Validación de celda disponible | Daniela Zapata  |  Exitoso |
| PT-07 | Creación de usuario y encriptación | Miledis Suarez |  Exitoso |
| PT-08 | Desactivación de usuario | Diego Ruiz |  Exitoso |
| PT-09 | Restricción en celda mantenimiento | Daniela Zapata   | Exitoso |
| PT-10 | Entrada exitosa en celda disponible |Milediss suarez  |  Exitoso |

### Evidencias

Todas las evidencias están organizadas en la carpeta `evidencias/`:

- **`01_interfaz/`**: Capturas de pantalla de la interfaz web
- **`02_mysql/`**: Capturas de consultas SQL en la base de datos

---

## Estructura del Proyecto

autos-colombia/
├── app/ # Código backend (Flask)
│ ├── init.py
│ ├── config.py
│ ├── extensions.py
│ ├── models.py
│ ├── rutas.py
│ └── servicios.py
├── database/ # Scripts de base de datos
├── evidencias/ # Documentación de pruebas
│ ├── 01_interfaz/ # Capturas de la interfaz web
│ └── 02_mysql/ # Capturas de consultas SQL
├── frontend/ # Interfaz web (HTML/CSS/JS)
│ └── index.html
├── tests/ # Tests unitarios
├── .gitignore
├── requirements.txt # Dependencias de Python
└── run.py # Archivo principal para ejecutar


---

##  Tecnologías

- **Backend:** Python 3.12 + Flask
- **Base de datos:** MySQL 8.x
- **Frontend:** HTML5 + CSS3 + JavaScript
- **Seguridad:** werkzeug (hash scrypt para contraseñas)
- **ORM:** SQLAlchemy

---

## Requisitos

- Python 3.12 instalado
- MySQL Server corriendo
- Base de datos `autos_colombia` creada

---

##  Cómo ejecutar

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Midyss/autos-colombia.git
   cd autos-colombia
