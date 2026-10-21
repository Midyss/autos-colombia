"""
Clase que representa un Vehículo en el parqueadero.
Actualizado para coincidir con la tabla Vehiculo de la BD.
"""


class Vehiculo:
    def __init__(self, id, placa, tipo, color):
        self.id = id
        self.placa = placa
        self.tipo = tipo
        self.color = color

    def __str__(self):
        return f"Vehículo {self.placa} ({self.tipo} - {self.color})"