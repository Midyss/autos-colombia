from datetime import date

class Contrato:
    def __init__(self, id, id_vehiculo, fecha_inicio, fecha_fin, estado):
        self.id = id
        self.id_vehiculo = id_vehiculo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado

    def esta_activo(self):
        hoy = date.today()
        return self.estado == 'Activo' and self.fecha_inicio <= hoy <= self.fecha_fin