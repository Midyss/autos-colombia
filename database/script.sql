-- BASE DE DATOS: Parqueadero Autos Colombia
-- Iteración 1: Gestión de entrada y salida


-- 1. Creamos la base de datos
CREATE DATABASE IF NOT EXISTS autos_colombia;
USE autos_colombia;

-- 2. Tabla de VEHICULOS
CREATE TABLE vehiculo (
    id_vehiculo INT AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(6) NOT NULL UNIQUE,
    tipo VARCHAR(20) NOT NULL,
    propietario VARCHAR(100) NOT NULL
);

-- 3. Tabla de CONTRATOS MENSUALES
CREATE TABLE contrato_mensual (
    id_contrato INT AUTO_INCREMENT PRIMARY KEY,
    id_vehiculo INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado ENUM('Activo', 'Vencido', 'Cancelado') DEFAULT 'Activo',
    FOREIGN KEY (id_vehiculo) REFERENCES vehiculo(id_vehiculo)
);

-- 4. Tabla de REGISTROS DE MOVIMIENTO
CREATE TABLE registro_movimiento (
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    id_vehiculo INT NOT NULL,
    fecha_entrada DATETIME NOT NULL,
    fecha_salida DATETIME NULL,
    FOREIGN KEY (id_vehiculo) REFERENCES vehiculo(id_vehiculo)
);

-- 5. Datos de prueba
INSERT INTO vehiculo (placa, tipo, propietario) VALUES
('ABC123', 'Automóvil', 'Carlos Pérez'),
('DEF456', 'Moto', 'Ana Gómez'),
('GHI789', 'Automóvil', 'Luis Martínez');

INSERT INTO contrato_mensual (id_vehiculo, fecha_inicio, fecha_fin, estado) VALUES
(1, '2026-10-01', '2026-10-31', 'Activo'),
(2, '2026-10-01', '2026-10-31', 'Activo'),
(3, '2026-09-01', '2026-09-30', 'Vencido');