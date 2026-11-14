from flask import Blueprint, request, jsonify, session, send_from_directory
from app.models import Usuario, LogAuditoria, Vehiculo, Contrato, Celda, Estancia
from app.extensions import db
from datetime import datetime, date
from app.servicios import ServicioParqueadero, ReglaNegocioError
import os

bp = Blueprint('parqueadero', __name__)


# ==========================================
# RUTA RAÍZ: Servir el frontend
# ==========================================

@bp.route('/')
def frontend_index():
    """Sirve el archivo index.html desde la carpeta frontend"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')


# ==========================================
# AUTENTICACIÓN
# ==========================================

@bp.route('/api/login', methods=['POST'])
def login():
    """Login unificado para Administrador y Operador"""
    datos = request.get_json()
    
    if not datos or 'usuario' not in datos or 'password' not in datos:
        return jsonify({'error': 'Usuario y contraseña son obligatorios'}), 422
    
    usuario = Usuario.query.filter_by(nombre_usuario=datos['usuario']).first()
    
    if usuario and usuario.check_password(datos['password']) and usuario.estado == 'Activo':
        session['usuario_id'] = usuario.id
        session['usuario_nombre'] = usuario.nombre_completo
        session['usuario_rol'] = usuario.rol
        
        # TEMPORAL: Log desactivado hasta resolver el problema de la columna 'estado'
        # log = LogAuditoria(
        #     id_usuario=usuario.id,
        #     fecha_hora=datetime.now(),
        #     accion='Inicio de sesión',
        #     estado='Exitoso',
        #     descripcion=f'Usuario {usuario.nombre_usuario} inició sesión'
        # )
        # db.session.add(log)
        # db.session.commit()
        
        return jsonify({
            'mensaje': 'Login exitoso',
            'id': usuario.id,
            'nombre_completo': usuario.nombre_completo,
            'nombre_usuario': usuario.nombre_usuario,
            'rol': usuario.rol,
            'estado': usuario.estado
        }), 200
    
    return jsonify({'error': 'Credenciales inválidas o usuario inactivo'}), 401


@bp.route('/api/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    # TEMPORAL: Log desactivado
    # if 'usuario_id' in session:
    #     log = LogAuditoria(
    #         id_usuario=session['usuario_id'],
    #         fecha_hora=datetime.now(),
    #         accion='Cierre de sesión',
    #         estado='Exitoso'
    #     )
    #     db.session.add(log)
    #     db.session.commit()
    
    session.clear()
    return jsonify({'mensaje': 'Sesión cerrada'}), 200


# ==========================================
# ENTRADA DE VEHÍCULOS (PT-01, PT-02, PT-03)
# ==========================================

@bp.route('/api/entrada', methods=['POST'])
def entrada():
    """Registrar entrada de vehículo"""
    datos = request.get_json()
    
    try:
        resultado = ServicioParqueadero.registrar_entrada(
            datos['placa'],
            datos['id_usuario']
        )
        
        # TEMPORAL: Log desactivado
        # log = LogAuditoria(
        #     id_usuario=datos['id_usuario'],
        #     fecha_hora=datetime.now(),
        #     accion='Registro de entrada',
        #     estado='Exitoso',
        #     descripcion=f'Vehículo {datos["placa"]} ingresó al parqueadero'
        # )
        # db.session.add(log)
        # db.session.commit()
        
        return jsonify({'message': resultado}), 200
    except ReglaNegocioError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# CONSULTA DE VEHÍCULOS PRESENTES (PT-04)
# ==========================================

@bp.route('/api/vehiculos-presentes', methods=['GET'])
def vehiculos_presentes():
    """Consultar vehículos presentes"""
    lista = ServicioParqueadero.consultar_vehiculos_presentes()
    return jsonify(lista), 200


# ==========================================
# GESTIÓN DE USUARIOS (PT-07, PT-08)
# ==========================================

@bp.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    """Listar todos los usuarios"""
    usuarios = Usuario.query.all()
    return jsonify([{
        'id': u.id,
        'nombre_completo': u.nombre_completo,
        'cedula': u.cedula,
        'nombre_usuario': u.nombre_usuario,
        'rol': u.rol,
        'estado': u.estado
    } for u in usuarios]), 200


@bp.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    """Crear nuevo usuario (PT-07)"""
    datos = request.get_json()
    
    if not datos:
        return jsonify({'error': 'Datos incompletos'}), 422
    
    campos_requeridos = ['nombre_completo', 'cedula', 'nombre_usuario', 'password', 'rol']
    for campo in campos_requeridos:
        if campo not in datos or not datos[campo].strip():
            return jsonify({'error': f'El campo {campo} es obligatorio'}), 422
    
    if Usuario.query.filter_by(nombre_usuario=datos['nombre_usuario'].strip()).first():
        return jsonify({'error': 'El nombre de usuario ya está registrado'}), 409
    
    if datos['rol'] not in ['Administrador', 'Operador']:
        return jsonify({'error': 'El rol debe ser Administrador u Operador'}), 422
    
    nuevo_usuario = Usuario(
        nombre_completo=datos['nombre_completo'].strip(),
        cedula=datos['cedula'].strip(),
        nombre_usuario=datos['nombre_usuario'].strip(),
        rol=datos['rol'],
        estado='Activo'
    )
    nuevo_usuario.set_password(datos['password'])
    
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    # TEMPORAL: Log desactivado
    # log = LogAuditoria(
    #     id_usuario=session.get('usuario_id'),
    #     fecha_hora=datetime.now(),
    #     accion='Creación de usuario',
    #     estado='Exitoso',
    #     descripcion=f'Usuario {nuevo_usuario.nombre_usuario} creado con rol {nuevo_usuario.rol}'
    # )
    # db.session.add(log)
    # db.session.commit()
    
    return jsonify({
        'mensaje': 'Usuario creado exitosamente',
        'id': nuevo_usuario.id
    }), 201


@bp.route('/api/usuarios/<int:id>/desactivar', methods=['PUT'])
def desactivar_usuario(id):
    """Desactivar usuario (PT-08)"""
    usuario = Usuario.query.get(id)
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    usuario.estado = 'Inactivo'
    db.session.commit()
    
    # TEMPORAL: Log desactivado
    # log = LogAuditoria(
    #     id_usuario=session.get('usuario_id'),
    #     fecha_hora=datetime.now(),
    #     accion='Desactivación de usuario',
    #     estado='Exitoso',
    #     descripcion=f'Usuario {usuario.nombre_completo} desactivado'
    # )
    # db.session.add(log)
    # db.session.commit()
    
    return jsonify({'mensaje': f'Usuario {usuario.nombre_completo} desactivado'}), 200


# ==========================================
# GESTIÓN DE CELDAS (PT-09, PT-10)
# ==========================================

@bp.route('/api/celdas', methods=['GET'])
def listar_celdas():
    """Listar todas las celdas"""
    celdas = Celda.query.all()
    return jsonify([{
        'id': c.id,
        'codigo': c.codigo,
        'tipo': c.tipo,
        'estado': c.estado
    } for c in celdas]), 200


@bp.route('/api/celdas/<int:id>/estado', methods=['PUT'])
def cambiar_estado_celda(id):
    """Cambiar estado de celda (PT-09, PT-10)"""
    celda = Celda.query.get(id)
    
    if not celda:
        return jsonify({'error': 'Celda no encontrada'}), 404
    
    datos = request.get_json()
    
    if not datos or 'estado' not in datos:
        return jsonify({'error': 'El campo estado es obligatorio'}), 422
    
    estados_validos = ['Disponible', 'Ocupada', 'Mantenimiento', 'Inhabilitada']
    if datos['estado'] not in estados_validos:
        return jsonify({'error': f'El estado debe ser uno de: {estados_validos}'}), 422
    
    celda.estado = datos['estado']
    db.session.commit()
    
    # TEMPORAL: Log desactivado
    # log = LogAuditoria(
    #     id_usuario=session.get('usuario_id'),
    #     fecha_hora=datetime.now(),
    #     accion='Cambio de estado de celda',
    #     estado='Exitoso',
    #     descripcion=f'Celda {celda.codigo} cambiada a {datos["estado"]}'
    # )
    # db.session.add(log)
    # db.session.commit()
    
    return jsonify({
        'mensaje': f'Celda {celda.codigo} actualizada a {datos["estado"]}'
    }), 200