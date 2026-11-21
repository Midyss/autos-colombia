from flask import Blueprint, request, jsonify, session, send_from_directory, render_template, redirect, url_for, flash
from app.models import Usuario, LogAuditoria, Vehiculo, Contrato, Celda, Estancia, Pago
from app.extensions import db
from datetime import datetime, date
from app.servicios import ServicioParqueadero, ReglaNegocioError, ServiciosPago
import os

bp = Blueprint('parqueadero', __name__)


# RUTA RAÍZ: Servir el frontend SPA

@bp.route('/')
def frontend_index():
    """Sirve el archivo index.html desde la carpeta frontend"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')


# AUTENTICACIÓN

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
    session.clear()
    return jsonify({'mensaje': 'Sesión cerrada'}), 
# ENTRADA DE VEHÍCULOS (Iteración 1)

@bp.route('/api/entrada', methods=['POST'])
def entrada():
    """Registrar entrada de vehículo"""
    datos = request.get_json()
    
    try:
        resultado = ServicioParqueadero.registrar_entrada(
            datos['placa'],
            datos['id_usuario']
        )
        return jsonify({'message': resultado}), 200
    except ReglaNegocioError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# CONSULTA DE VEHÍCULOS PRESENTES (Iteración 1)

@bp.route('/api/vehiculos-presentes', methods=['GET'])
def vehiculos_presentes():
    """Consultar vehículos presentes"""
    lista = ServicioParqueadero.consultar_vehiculos_presentes()
    return jsonify(lista), 200


# GESTIÓN DE USUARIOS (Iteración 2)

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
    """Crear nuevo usuario"""
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
    
    return jsonify({
        'mensaje': 'Usuario creado exitosamente',
        'id': nuevo_usuario.id
    }), 201

@bp.route('/api/usuarios/<int:id>/desactivar', methods=['PUT'])
def desactivar_usuario(id):
    """Desactivar usuario"""
    usuario = Usuario.query.get(id)
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    usuario.estado = 'Inactivo'
    db.session.commit()
    
    return jsonify({'mensaje': f'Usuario {usuario.nombre_completo} desactivado'}), 200


# GESTIÓN DE CELDAS (Iteración 2)

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
    """Cambiar estado de celda"""
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
    
    return jsonify({
        'mensaje': f'Celda {celda.codigo} actualizada a {datos["estado"]}'
    }), 200


# API DE PAGOS (Iteración 3) 


@bp.route('/api/pagos/consultar', methods=['GET'])
def api_consultar_contrato():
    """Consulta el contrato de un vehículo por placa"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    placa = request.args.get('placa', '').strip().upper()
    if not placa:
        return jsonify({'error': 'La placa es obligatoria'}), 400
    
    contrato_info, error = ServiciosPago.consultar_contrato(placa)
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify(contrato_info), 200


@bp.route('/api/pagos/registrar', methods=['POST'])
def api_registrar_pago():
    """Registra un pago de mensualidad"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    datos = request.get_json()
    if not datos:
        return jsonify({'error': 'Datos incompletos'}), 422
    
    placa = datos.get('placa', '').strip().upper()
    valor = datos.get('valor')
    forma_pago = datos.get('forma_pago', 'Efectivo')
    fecha_pago_str = datos.get('fecha_pago')
    id_usuario = session['usuario_id']
    
    if not placa or not valor:
        return jsonify({'error': 'Placa y valor son obligatorios'}), 422
    
    try:
        valor = float(valor)
    except ValueError:
        return jsonify({'error': 'El valor debe ser un número'}), 422
    
    fecha_pago = None
    if fecha_pago_str:
        try:
            fecha_pago = datetime.strptime(fecha_pago_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido'}), 422
    
    pago, mensaje = ServiciosPago.registrar_pago(
        placa, valor, forma_pago, id_usuario, fecha_pago
    )
    
    if pago:
        return jsonify({'success': True, 'data': pago, 'mensaje': mensaje}), 201
    else:
        return jsonify({'success': False, 'error': mensaje}), 400


@bp.route('/api/pagos/historial', methods=['GET'])
def api_historial_pagos():
    """Consulta el historial de pagos de un vehículo"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    placa = request.args.get('placa', '').strip().upper()
    if not placa:
        return jsonify({'error': 'La placa es obligatoria'}), 400
    
    historial, error = ServiciosPago.consultar_historial(placa)
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify(historial), 200


@bp.route('/api/comprobante/<numero_recibo>', methods=['GET'])
def api_comprobante(numero_recibo):
    """Obtiene los datos de un comprobante"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    pago = Pago.query.filter_by(numero_recibo=numero_recibo).first()
    if not pago:
        return jsonify({'error': 'Comprobante no encontrado'}), 404
    
    return jsonify(pago.to_dict()), 200



# RUTAS LEGACY (render_template) - Se mantienen por compatibilidad


@bp.route('/pagos', methods=['GET', 'POST'])
def pagos():
    """Página de gestión de pagos (versión legacy con templates)"""
    if 'usuario_id' not in session:
        return redirect(url_for('parqueadero.frontend_index'))
    
    contrato_info = None
    historial = []
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        placa = request.form.get('placa')
        id_usuario = session['usuario_id']
        
        if accion == 'buscar':
            contrato_info, error = ServiciosPago.consultar_contrato(placa)
            if error:
                flash(error, 'error')
        
        elif accion == 'registrar':
            try:
                valor = float(request.form.get('valor'))
            except ValueError:
                flash("El valor debe ser un número válido", 'error')
                return redirect(url_for('parqueadero.pagos'))
            
            forma_pago = request.form.get('forma_pago')
            fecha_pago_str = request.form.get('fecha_pago')
            
            fecha_pago = None
            if fecha_pago_str:
                fecha_pago = datetime.strptime(fecha_pago_str, '%Y-%m-%d').date()
            
            pago, mensaje = ServiciosPago.registrar_pago(
                placa, valor, forma_pago, id_usuario, fecha_pago
            )
            
            if pago:
                flash(mensaje, 'success')
            else:
                flash(mensaje, 'error')
            
            contrato_info, _ = ServiciosPago.consultar_contrato(placa)
        
        elif accion == 'historial':
            historial, error = ServiciosPago.consultar_historial(placa)
            if error:
                flash(error, 'error')
    
    return render_template('pagos.html', 
                          contrato=contrato_info, 
                          historial=historial,
                          usuario=session.get('usuario_nombre'))

@bp.route('/comprobante/<numero_recibo>')
def comprobante(numero_recibo):
    """Vista del comprobante de pago (versión legacy)"""
    pago = Pago.query.filter_by(numero_recibo=numero_recibo).first()
    if not pago:
        flash("Comprobante no encontrado", 'error')
        return redirect(url_for('parqueadero.pagos'))
    
    return render_template('comprobante.html', pago=pago.to_dict())