"""
Lógica principal del sistema: valida mensualidad, 
registra entradas y salidas en la tabla estancia.
Actualizado para usar las tablas: Vehiculo, Contrato, Celdas, estancia.
"""
from datetime import datetime
from .conexion import conectar_bd
from .vehiculo import Vehiculo
from .contrato import Contrato


class ControlAcceso:
    def __init__(self):
        self.conexion = conectar_bd()
        self.id_operador = 1  # Usamos el operador "Ana López" de la BD

    def _buscar_vehiculo_por_placa(self, placa):
        """Busca un vehículo en la BD por su placa."""
        cursor = self.conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Vehiculo WHERE placa = %s", (placa,))
        resultado = cursor.fetchone()
        cursor.close()
        if resultado:
            return Vehiculo(**resultado)
        return None

    def _buscar_contrato_activo(self, id_vehiculo):
        """Busca si el vehículo tiene un contrato mensual activo."""
        cursor = self.conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM Contrato 
            WHERE id_vehiculo = %s AND estado = 'Activo'
        """, (id_vehiculo,))
        resultado = cursor.fetchone()
        cursor.close()
        if resultado:
            contrato = Contrato(**resultado)
            if contrato.esta_activo():
                return contrato
        return None

    def _buscar_celda_disponible(self, tipo_vehiculo):
        """Busca una celda disponible del tipo correspondiente."""
        cursor = self.conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM Celdas 
            WHERE tipo = %s AND estado = 'Disponible' 
            LIMIT 1
        """, (tipo_vehiculo,))
        resultado = cursor.fetchone()
        cursor.close()
        if resultado:
            return resultado  # Retornamos el diccionario directamente
        return None

    def _vehiculo_dentro(self, placa):
        """Verifica si el vehículo ya está adentro (tiene estancia abierta)."""
        cursor = self.conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM estancia e
            JOIN Vehiculo v ON e.id_vehiculo = v.id
            WHERE v.placa = %s AND e.salida IS NULL
        """, (placa,))
        return cursor.fetchone()[0] > 0

    def registrar_entrada(self, placa):
        """Registra la entrada de un vehículo."""
        print(f"\n Intentando registrar entrada de placa: {placa}")

        # Validación 1: ¿Existe el vehículo?
        vehiculo = self._buscar_vehiculo_por_placa(placa)
        if not vehiculo:
            print(f" RECHAZADO: El vehículo {placa} NO está registrado.")
            return False

        # Validación 2: ¿Tiene mensualidad activa?
        contrato = self._buscar_contrato_activo(vehiculo.id)
        if not contrato:
            print(f" RECHAZADO: El vehículo {placa} NO tiene mensualidad activa.")
            return False

        # Validación 3: ¿Ya está adentro?
        if self._vehiculo_dentro(placa):
            print(f"ATENCIÓN: El vehículo {placa} YA está dentro.")
            return False

        # Validación 4: ¿Hay celda disponible?
        celda = self._buscar_celda_disponible(vehiculo.tipo)
        if not celda:
            print(f" RECHAZADO: No hay celdas disponibles para {vehiculo.tipo}.")
            return False

        # TODO OK: Registramos la entrada
        cursor = self.conexion.cursor()
        
        # 1. Crear el registro en la tabla estancia
        cursor.execute("""
            INSERT INTO estancia (id_vehiculo, id_celda, id_operador, entrada)
            VALUES (%s, %s, %s, %s)
        """, (vehiculo.id, celda['id'], self.id_operador, datetime.now()))
        
        # 2. Cambiar estado de la celda a Ocupada
        cursor.execute("UPDATE Celdas SET estado = 'Ocupada' WHERE id = %s", (celda['id'],))
        
        self.conexion.commit()
        cursor.close()

        print(f" ENTRADA REGISTRADA: {vehiculo} asignado a Celda {celda['codigo']}.")
        return True

    def registrar_salida(self, placa):
        """Registra la salida de un vehículo."""
        print(f"\n Registrando salida de placa: {placa}")

        vehiculo = self._buscar_vehiculo_por_placa(placa)
        if not vehiculo:
            print(f" El vehículo {placa} no existe.")
            return False

        if not self._vehiculo_dentro(placa):
            print(f" El vehículo {placa} NO está dentro.")
            return False

        cursor = self.conexion.cursor()
        
        # 1. Buscar la celda que está ocupando
        cursor.execute("""
            SELECT id_celda FROM estancia 
            WHERE id_vehiculo = %s AND salida IS NULL
        """, (vehiculo.id,))
        id_celda = cursor.fetchone()[0]

        # 2. Cerrar la estancia (registrar salida)
        cursor.execute("""
            UPDATE estancia 
            SET salida = %s
            WHERE id_vehiculo = %s AND salida IS NULL
        """, (datetime.now(), vehiculo.id))
        
        # 3. Liberar la celda
        cursor.execute("UPDATE Celdas SET estado = 'Disponible' WHERE id = %s", (id_celda,))
        
        self.conexion.commit()
        cursor.close()

        print(f" SALIDA REGISTRADA: {vehiculo} salió. Celda liberada.")
        return True

    def consultar_cupos(self):
        """Muestra cuántos cupos hay disponibles."""
        cursor = self.conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM Celdas WHERE estado = 'Disponible'")
        disponibles = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Celdas")
        total = cursor.fetchone()[0]
        print(f"\n CUPOS: {disponibles} disponibles de {total} totales.")
        cursor.close()
        return disponibles

    def cerrar_conexion(self):
        """Cierra la conexión con la base de datos."""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("\n Conexión cerrada.")