from app.models import db, Vehiculo, Contrato, Celda, Estancia, Usuario, LogAuditoria, Pago
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash
import random


# Excepción personalizada para errores de reglas de negocio
class ReglaNegocioError(Exception):
    pass


# CLASE 1: ServicioParqueadero (Iteraciones 1 y 2)

class ServicioParqueadero:

    @staticmethod
    def registrar_entrada(placa, id_usuario):
        """
        Registra la entrada de un vehículo al parqueadero.
        - placa: placa del vehículo (ej: 'MKT-456')
        - id_usuario: ID del operador que está registrando (TRAZABILIDAD REAL)
        """
        # 1. Buscar el vehículo por placa
        vehiculo = Vehiculo.query.filter_by(placa=placa.upper()).first()
        if not vehiculo:
            raise ReglaNegocioError("Vehículo no registrado en el sistema")

        # 2. Validar que tenga contrato (mensualidad) activo
        contrato_activo = Contrato.query.filter_by(
            id_vehiculo=vehiculo.id,
            estado='Activo'
        ).first()

        if not contrato_activo:
            raise ReglaNegocioError("El vehículo no tiene un contrato activo")

        # Validar que la fecha de fin no haya pasado
        if contrato_activo.fecha_fin < date.today():
            raise ReglaNegocioError("La mensualidad del vehículo está vencida")

        # 3. Validar que el vehículo NO esté ya dentro del parqueadero
        estancia_abierta = Estancia.query.filter_by(
            id_vehiculo=vehiculo.id,
            fecha_salida=None
        ).first()

        if estancia_abierta:
            raise ReglaNegocioError("El vehículo ya se encuentra dentro del parqueadero")

        # 4. Buscar una celda disponible del tipo correcto (Auto o Moto)
        # IMPORTANTE: with_for_update() bloquea la celda para evitar que dos
        # operadores la asignen al mismo tiempo (Protección de concurrencia RNF-05)
        celda = Celda.query.filter_by(
            tipo=vehiculo.tipo,
            estado='Disponible'
        ).with_for_update().first()

        if not celda:
            raise ReglaNegocioError(f"No hay celdas disponibles para {vehiculo.tipo}")

        # 5. Crear la estancia con TRAZABILIDAD REAL (id_usuario, no un '1' fijo)
        nueva_estancia = Estancia(
            id_vehiculo=vehiculo.id,
            id_celda=celda.id,
            id_usuario=id_usuario,
            fecha_entrada=datetime.now()
        )

        # Cambiar el estado de la celda a 'Ocupada'
        celda.estado = 'Ocupada'

        # Guardar los cambios en la base de datos
        db.session.add(nueva_estancia)
        db.session.commit()

        # 6. Registrar en log de auditoría
        log = LogAuditoria(
            id_usuario=id_usuario,
            fecha_hora=datetime.now(),
            accion='Registro de entrada',
            estado='Exitoso',
            descripcion=f'Vehículo {placa.upper()} asignado a celda {celda.codigo}'
        )
        db.session.add(log)
        db.session.commit()

        return f"Entrada exitosa. Vehículo {placa.upper()} asignado a la celda {celda.codigo}"

    @staticmethod
    def consultar_vehiculos_presentes():
        """
        Lista todos los vehículos que están actualmente dentro del parqueadero.
        Muestra: placa, tipo, celda asignada, operador que registró y hora de entrada.
        """
        estancias = Estancia.query.filter_by(fecha_salida=None).all()

        resultado = []
        for e in estancias:
            vehiculo = Vehiculo.query.get(e.id_vehiculo)
            celda = Celda.query.get(e.id_celda)
            usuario = Usuario.query.get(e.id_usuario)

            resultado.append({
                'placa': vehiculo.placa,
                'tipo': vehiculo.tipo,
                'celda': celda.codigo,
                'operador': usuario.nombre_completo,
                'fecha_entrada': e.fecha_entrada.strftime('%Y-%m-%d %H:%M')
            })

        return resultado

    @staticmethod
    def crear_usuario(nombre_completo, cedula, nombre_usuario, password, rol):
        """
        Crea un nuevo usuario en el sistema (PT-07).
        """
        # Validar que el nombre de usuario no exista
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            raise ReglaNegocioError("El nombre de usuario ya está registrado")

        # Roles en formato capitalizado (coincide con el frontend y BD)
        if rol not in ['Administrador', 'Operador']:
            raise ReglaNegocioError("El rol debe ser Administrador u Operador")

        nuevo_usuario = Usuario(
            nombre_completo=nombre_completo,
            cedula=cedula,
            nombre_usuario=nombre_usuario,
            rol=rol,
            estado='Activo'
        )
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        return f"Usuario {nombre_usuario} creado exitosamente"

    @staticmethod
    def desactivar_usuario(id_usuario):
        """
        Desactiva un usuario (PT-08).
        """
        usuario = Usuario.query.get(id_usuario)

        if not usuario:
            raise ReglaNegocioError("Usuario no encontrado")

        if usuario.estado == 'Inactivo':
            raise ReglaNegocioError("El usuario ya está inactivo")

        usuario.estado = 'Inactivo'
        db.session.commit()

        return f"Usuario {usuario.nombre_completo} desactivado"

    @staticmethod
    def cambiar_estado_celda(id_celda, nuevo_estado):
        """
        Cambia el estado de una celda (PT-09, PT-10).
        """
        celda = Celda.query.get(id_celda)

        if not celda:
            raise ReglaNegocioError("Celda no encontrada")

        estados_validos = ['Disponible', 'Ocupada', 'Mantenimiento', 'Inhabilitada']
        if nuevo_estado not in estados_validos:
            raise ReglaNegocioError(f"Estado inválido. Debe ser uno de: {estados_validos}")

        celda.estado = nuevo_estado
        db.session.commit()

        return f"Celda {celda.codigo} actualizada a {nuevo_estado}"


# CLASE 2: ServiciosPago (Iteración 3)

class ServiciosPago:

    @staticmethod
    def consultar_contrato(placa):
        """Muestra el corte actual antes de registrar el pago"""
        vehiculo = Vehiculo.query.filter_by(placa=placa.upper()).first()
        if not vehiculo:
            return None, "Vehículo no registrado en el sistema"
        
        contrato = Contrato.query.filter_by(id_vehiculo=vehiculo.id).first()
        if not contrato:
            return None, "El vehículo no tiene contrato"
        
        hoy = datetime.now().date()
        dias_restantes = (contrato.fecha_fin - hoy).days
        
        if dias_restantes < 0:
            estado = "Vencido"
        elif dias_restantes <= 7:
            estado = "Por vencer"
        else:
            estado = "Al día"
        
        return {
            'placa': vehiculo.placa,
            'tipo': vehiculo.tipo,
            'propietario': vehiculo.propietario,
            'fecha_fin': contrato.fecha_fin.strftime('%d/%m/%Y'),
            'dias_restantes': dias_restantes,
            'estado': estado,
            'id_contrato': contrato.id,
            'valor_mensual': 250000 if vehiculo.tipo == 'Automóvil' else 100000
        }, None
    
    @staticmethod
    def registrar_pago(placa, valor, forma_pago, id_usuario, fecha_pago=None):
        """
         REGLA DE NEGOCIO (RNF-01):
        El periodo cubierto se calcula desde fecha_fin del contrato + 1 día,
        NO desde la fecha de pago. Así el cliente que paga anticipado no pierde días.
        """
        vehiculo = Vehiculo.query.filter_by(placa=placa.upper()).first()
        if not vehiculo:
            return None, "El vehículo no está registrado en el sistema"
        
        # BLOQUEO FOR UPDATE (RNF-05 concurrencia)
        contrato = db.session.query(Contrato).filter_by(
            id_vehiculo=vehiculo.id
        ).with_for_update().first()
        
        if not contrato:
            return None, "El vehículo no tiene contrato registrado"
        
        hoy = datetime.now().date()
        fecha_pago_real = fecha_pago if fecha_pago else hoy
        
        # Validar contrato vencido (PT-13)
        if contrato.fecha_fin < hoy and fecha_pago_real > contrato.fecha_fin:
            return None, f"El contrato venció el {contrato.fecha_fin.strftime('%d/%m/%Y')}. No se puede registrar pago, debe regularizar primero."
        
        # CÁLCULO DEL PERIODO DESDE EL CORTE, NO DESDE LA FECHA DE PAGO
        periodo_inicio = contrato.fecha_fin + timedelta(days=1)
        periodo_fin = periodo_inicio + timedelta(days=30)
        
        numero_recibo = f"REC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        nuevo_pago = Pago(
            id_contrato=contrato.id,
            valor=valor,
            fecha_pago=fecha_pago_real,
            forma_pago=forma_pago,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
            numero_recibo=numero_recibo,
            id_usuario=id_usuario
        )
        
        db.session.add(nuevo_pago)
        contrato.fecha_fin = periodo_fin
        
        # Trazabilidad en log_auditoria
        log = LogAuditoria(
            id_usuario=id_usuario,
            accion=f"Pago registrado placa {placa}. Recibo {numero_recibo}. Periodo {periodo_inicio} a {periodo_fin}",
            fecha_hora=datetime.utcnow()
        )
        db.session.add(log)
        
        db.session.commit()
        
        mensaje = (f"Pago registrado. Recibo: {numero_recibo}. "
                   f"Periodo cubierto: {periodo_inicio.strftime('%d/%m/%Y')} al {periodo_fin.strftime('%d/%m/%Y')}")
        
        return nuevo_pago.to_dict(), mensaje

    @staticmethod
    def consultar_historial(placa):
        """
        Consulta el historial de pagos de un vehículo por placa.
        Retorna una lista de pagos con sus datos y el nombre del operador.
        """
        vehiculo = Vehiculo.query.filter_by(placa=placa.upper()).first()
        if not vehiculo:
            return None, "Vehículo no registrado en el sistema"
        
        # Buscar el contrato del vehículo
        contrato = Contrato.query.filter_by(id_vehiculo=vehiculo.id).first()
        if not contrato:
            return None, "El vehículo no tiene contrato"
        
        # Buscar todos los pagos de ese contrato, ordenados del más reciente al más antiguo
        pagos = Pago.query.filter_by(id_contrato=contrato.id)\
            .order_by(Pago.fecha_pago.desc()).all()
        
        resultado = []
        for p in pagos:
            operador = Usuario.query.get(p.id_usuario)
            resultado.append({
                'numero_recibo': p.numero_recibo,
                'fecha_pago': str(p.fecha_pago),
                'valor': float(p.valor),
                'forma_pago': p.forma_pago,
                'periodo_inicio': str(p.periodo_inicio) if p.periodo_inicio else '-',
                'periodo_fin': str(p.periodo_fin) if p.periodo_fin else '-',
                'operador': operador.nombre_completo if operador else 'Desconocido'
            })
        
        return resultado, None