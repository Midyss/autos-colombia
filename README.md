#  Autos Colombia - Sistema de Gestión de Parqueadero

Sistema de información completo para la gestión de un parqueadero que opera por **mensualidad**. Desarrollado con arquitectura en capas usando Python, Flask, MySQL y JavaScript.



##  Información del Proyecto

| Campo | Detalle |
|-------|---------|
| **Proyecto** | Parqueadero "Autos Colombia" |
| **Asignatura** | Ingeniería de Software |
| **Grupo** | PREICA2602B020053 |
| **Docente** | Reinaldo Rojas López |
| **Institución** | Institución Universitaria Digital de Antioquia |
| **Fecha** | Noviembre 2026 |



## 👥 Equipo de Desarrollo

- **Miledis Suárez Pérez** 
- **Diego Andrés Ruiz Rodríguez** 
- **Erika Daniela Zapata Molina** 



##  Iteraciones del Proyecto

###  Iteración 1 - Registro de Entrada y Salida
**Rama:** `main`

- Registro de entrada de vehículos con validación de mensualidad
- Registro de salida con cálculo de tiempo de permanencia
- Control de aforo (cupos disponibles por tipo de vehículo)
- Bloqueo automático de vehículos sin contrato activo
- Asignación inteligente de celdas (Automóvil / Moto)

### Iteración 2 - Gestión de Usuarios y Celdas
**Rama:** `main`

- CRUD de usuarios (Administrador y Operador)
- Autenticación con contraseña encriptada (bcrypt)
- Gestión de celdas (Disponible, Ocupada, Mantenimiento, Inhabilitada)
- **Trazabilidad real**: cada acción queda vinculada al ID del operador
- **Bloqueo FOR UPDATE** para prevenir conflictos de concurrencia
- Log de auditoría en tabla `log_auditoria`

###  Iteración 3 - Gestión de Pagos  
**Rama:** `iteracion-3`

- Registro de pagos mensuales (Efectivo, QR, Consignación)
- Consulta de estado de contratos (Al día / Por vencer / Vencido)
- Historial de pagos por vehículo
- Generación de comprobantes en pantalla
- **Regla de negocio clave**: el periodo se calcula desde el corte del contrato, NO desde la fecha de pago




## Arquitectura del Sistema

autos-colombia2/
├── app/
│ ├── models.py (Modelos ORM: Usuario, Vehiculo, Contrato, Pago, etc.)
│ ├── servicios.py (Lógica de negocio: ServicioParqueadero, ServiciosPago)
│ ├── rutas.py (Endpoints API REST - Flask Blueprint)
│ └── extensions.py (Configuración SQLAlchemy)
├── frontend/
│ └── index.html (Interfaz SPA con JavaScript puro)
├── database/
│ └── script.sql (Script de creación de BD)
├── evidencias/
│ ├── 01_entrada/ (Capturas Iteración 1)
│ ├── 02_mysql/ (Capturas Iteración 2)
│ └── 04_pagos/ (Capturas Iteración 3 - PT-11 a PT-15)
├── requirements.txt (Dependencias Python)
├── run.py (Punto de entrada de la aplicación)
└── README.md 


