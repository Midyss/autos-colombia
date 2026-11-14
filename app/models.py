from datetime import datetime
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


# 1. Tabla de Usuarios
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column('password', db.String(255), nullable=False)
    rol = db.Column(db.Enum('Administrador', 'Operador'), default='Operador')
    estado = db.Column(db.Enum('Activo', 'Inactivo'), default='Activo')
    
    # Métodos para encriptar y verificar contraseñas
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'


# 2. Tabla de Vehículos
class Vehiculo(db.Model):
    __tablename__ = 'vehiculo'
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    propietario = db.Column(db.String(100))
    
    # Relación: Un vehículo puede tener muchos contratos
    contratos = db.relationship('Contrato', backref='vehiculo', lazy=True)
    
    def __repr__(self):
        return f'<Vehiculo {self.placa}>'


# 3. Tabla de Contratos
class Contrato(db.Model):
    __tablename__ = 'contrato'
    id = db.Column(db.Integer, primary_key=True)
    id_vehiculo = db.Column(db.Integer, db.ForeignKey('vehiculo.id'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    estado = db.Column(db.Enum('Activo', 'Vencido', 'Cancelado'), default='Activo')
    
    def __repr__(self):
        return f'<Contrato {self.id} - Vehículo {self.id_vehiculo}>'


# 4. Tabla de Celdas
class Celda(db.Model):
    __tablename__ = 'celda'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), default='Disponible')
    
    def __repr__(self):
        return f'<Celda {self.codigo}>'


# 5. Tabla de Estancias (Trazabilidad real con id_usuario)
class Estancia(db.Model):
    __tablename__ = 'estancia'
    id = db.Column(db.Integer, primary_key=True)
    id_vehiculo = db.Column(db.Integer, db.ForeignKey('vehiculo.id'), nullable=False)
    id_celda = db.Column(db.Integer, db.ForeignKey('celda.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_salida = db.Column(db.DateTime, nullable=True)
    
    # Relaciones para facilitar consultas
    vehiculo = db.relationship('Vehiculo', backref='estancias')
    celda = db.relationship('Celda', backref='estancias')
    usuario = db.relationship('Usuario', backref='estancias')
    
    def __repr__(self):
        return f'<Estancia {self.id} - Vehículo {self.id_vehiculo}>'


# 6. Tabla de Log de Auditoría 
class LogAuditoria(db.Model):
    __tablename__ = 'log_auditoria'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    accion = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(50), default='Exitoso')
    descripcion = db.Column(db.String(500), nullable=True)
    
    # Relación con Usuario
    usuario = db.relationship('Usuario', backref='logs')
    
    def __repr__(self):
        return f'<Log {self.id} - {self.accion}>'