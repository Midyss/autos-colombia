-- BASE DE DATOS: Parqueadero Autos Colombia
-- Iteración 1: Gestión de entrada y salida de vehículos
-- Autores: Miledis Suarez, Diego Ruiz, Erika Zapata
-- Fecha: Octubre 2026

-- 1. Crear la base de datos
CREATE DATABASE IF NOT EXISTS autos_colombia;
USE autos_colombia;

-- 2. Tabla de Vehículos
CREATE TABLE Vehiculo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(10) NOT NULL UNIQUE,
    tipo VARCHAR(20) NOT NULL,
    color VARCHAR(20) NOT NULL
);

-- 3. Tabla de Celdas
CREATE TABLE Celdas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    tipo VARCHAR(20) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Disponible'
);

-- 4. Tabla de Contratos (Mensualidad)
CREATE TABLE Contrato (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_vehiculo INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activo',
    FOREIGN KEY (id_vehiculo) REFERENCES Vehiculo(id)
);

-- 5. Tabla de Estancias (Entradas y Salidas)
CREATE TABLE estancia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_vehiculo INT NOT NULL,
    id_celda INT NOT NULL,
    id_operador INT NOT NULL DEFAULT 1,
    entrada DATETIME NOT NULL,
    salida DATETIME NULL,
    FOREIGN KEY (id_vehiculo) REFERENCES Vehiculo(id),
    FOREIGN KEY (id_celda) REFERENCES Celdas(id)
);

-- 6. Datos de prueba
INSERT INTO Vehiculo (placa, tipo, color) VALUES 
('MKT-456', 'Automóvil', 'Gris'),
('LOP-234', 'Moto', 'Negra'),
('QRS-890', 'Automóvil', 'Blanco');

INSERT INTO Celdas (codigo, tipo, estado) VALUES 
('A-15', 'Automóvil', 'Disponible'),
('A-22', 'Automóvil', 'Disponible'),
('M-08', 'Moto', 'Disponible');

INSERT INTO Contrato (id_vehiculo, fecha_inicio, fecha_fin, estado) VALUES 
(1, '2026-10-01', '2026-11-30', 'Activo'),
(2, '2026-10-01', '2026-12-15', 'Activo'),
(3, '2026-09-01', '2026-09-30', 'Vencido');