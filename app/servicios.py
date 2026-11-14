from app.models import db, Vehiculo, Contrato, Celda, Estancia, Usuario, LogAuditoria
from datetime import date, datetime
from werkzeug.security import generate_password_hash


# Excepción personalizada para errores de reglas de negocio
class ReglaNegocioError(Exception):
    pass


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

        #  roles en formato capitalizado (coincide con el frontend y BD)
        if rol not in ['Administrador', 'Operador']:
            raise ReglaNegocioError("El rol debe ser Administrador u Operador")

        #  usar 'password' en lugar de 'password_hash'
        nuevo_usuario = Usuario(
            nombre_completo=nombre_completo,
            cedula=cedula,
            nombre_usuario=nombre_usuario,
            rol=rol,
            estado='Activo'
        )
        nuevo_usuario.set_password(password)  # ← Usa el método del modelo

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