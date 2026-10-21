"""
Programa principal del Parqueadero Autos Colombia.
Iteración 1: Gestión de entrada y salida de vehículos.
"""
from src.control_acceso import ControlAcceso


def menu():
    sistema = ControlAcceso()

    while True:
        print("\n" + "=" * 50)
        print("   PARQUEADERO AUTOS COLOMBIA")
        print("=" * 50)
        print("1. Registrar ENTRADA de vehículo")
        print("2. Registrar SALIDA de vehículo")
        print("3. Consultar cupos disponibles")
        print("4. Salir")
        opcion = input("\nSeleccione una opción: ")

        if opcion == '1':
            placa = input("Ingrese la placa del vehículo: ").upper()
            sistema.registrar_entrada(placa)

        elif opcion == '2':
            placa = input("Ingrese la placa del vehículo: ").upper()
            sistema.registrar_salida(placa)

        elif opcion == '3':
            sistema.consultar_cupos()

        elif opcion == '4':
            sistema.cerrar_conexion()
            print(" ¡Hasta pronto!")
            break

        else:
            print(" Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    menu()