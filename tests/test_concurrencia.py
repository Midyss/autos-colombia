"""
Prueba de Concurrencia - RNF-05
Simula 2 operadores registrando entradas simultáneamente
para validar que no se asignen duplicados de celda.

ESCENARIO: Ambos vehículos son de tipo Automóvil y solo hay 1 celda
disponible de ese tipo (A-22), por lo que solo un operador podrá
registrar la entrada exitosamente.
"""

import sys
import os
import threading
import time

# Agregar la carpeta raíz al path para poder importar app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import Vehiculo, Celda, Estancia, Usuario, Contrato
from app.servicios import ServicioParqueadero, ReglaNegocioError
from datetime import datetime

# Lista para guardar resultados de cada hilo
resultados = []

# Crear la aplicación una sola vez
app = create_app()

def operador_1():
    """Simula al operador Sofia Madariaga (id=2) registrando MKT-456 (Automóvil)"""
    # Cada hilo necesita su propio contexto de aplicación
    with app.app_context():
        try:
            print(f"[Operador 1 - Sofia] Intentando registrar entrada de placa MKT-456 (Automóvil)...")
            resultado = ServicioParqueadero.registrar_entrada("MKT-456", 2)  # Sofia tiene id=2
            print(f"[Operador 1 - Sofia] ✅ ÉXITO: {resultado}")
            resultados.append(("Operador 1 (Sofia)", True, resultado))
        except ReglaNegocioError as e:
            print(f"[Operador 1 - Sofia]  ERROR: {e}")
            resultados.append(("Operador 1 (Sofia)", False, str(e)))
        except Exception as e:
            print(f"[Operador 1 - Sofia]  EXCEPCIÓN: {e}")
            resultados.append(("Operador 1 (Sofia)", False, str(e)))

def operador_2():
    """Simula al operador Patricia Hernandez (id=3) registrando QRS-890 (Automóvil)"""
    # Cada hilo necesita su propio contexto de aplicación
    with app.app_context():
        try:
            print(f"[Operador 2 - Patricia] Intentando registrar entrada de placa QRS-890 (Automóvil)...")
            resultado = ServicioParqueadero.registrar_entrada("QRS-890", 3)  # Patricia tiene id=3
            print(f"[Operador 2 - Patricia]  ÉXITO: {resultado}")
            resultados.append(("Operador 2 (Patricia)", True, resultado))
        except ReglaNegocioError as e:
            print(f"[Operador 2 - Patricia] ERROR: {e}")
            resultados.append(("Operador 2 (Patricia)", False, str(e)))
        except Exception as e:
            print(f"[Operador 2 - Patricia]  EXCEPCIÓN: {e}")
            resultados.append(("Operador 2 (Patricia)", False, str(e)))


def ejecutar_prueba_concurrencia():
    """Ejecuta la prueba de concurrencia"""
    print("=" * 70)
    print("PRUEBA DE CONCURRENCIA - RNF-05")
    print("Simulación: 2 operadores intentando asignar la MISMA celda simultáneamente")
    print("Ambos vehículos son tipo Automóvil, solo hay 1 celda disponible (A-22)")
    print("=" * 70)
    print()
    
    # Limpiar resultados anteriores
    resultados.clear()
    
    # Preparar el contexto de la aplicación Flask para la verificación inicial
    with app.app_context():
        # Verificar que haya celdas disponibles antes de la prueba
        celdas_disponibles_auto = Celda.query.filter_by(tipo='Automóvil', estado='Disponible').count()
        print(f" Celdas disponibles de tipo Automóvil antes de la prueba: {celdas_disponibles_auto}")
        print()
        
        if celdas_disponibles_auto != 1:
            print("ADVERTENCIA: Se esperaba 1 celda disponible de Automóvil,")
            print(f"   pero hay {celdas_disponibles_auto}. La prueba puede no demostrar la concurrencia correctamente.")
            print("   Ejecuta el script SQL para dejar solo 1 celda disponible.")
            print()
        
        # Crear los hilos (simulando operadores simultáneos)
        hilo1 = threading.Thread(target=operador_1)
        hilo2 = threading.Thread(target=operador_2)
        
        print(" Iniciando ambos operadores al mismo tiempo...")
        print()
        
        # Iniciar ambos hilos simultáneamente
        hilo1.start()
        hilo2.start()
        
        # Esperar a que ambos terminen
        hilo1.join()
        hilo2.join()
        
        print()
        print("=" * 70)
        print("RESULTADOS DE LA PRUEBA")
        print("=" * 70)
        
        # Mostrar resultados
        exitos = 0
        fallos = 0
        for operador, exito, mensaje in resultados:
            estado = " EXITO" if exito else " FALLIDO"
            print(f"{estado} | {operador}: {mensaje}")
            if exito:
                exitos += 1
            else:
                fallos += 1
        
        print()
        print(f"Total de entradas exitosas: {exitos}")
        print(f"Total de entradas fallidas: {fallos}")
        print()
        
        # Verificar en la base de datos que no haya duplicados
        print(" Verificación en base de datos:")
        estancias = Estancia.query.filter_by(fecha_salida=None).all()
        celdas_ocupadas = [e.id_celda for e in estancias]
        celdas_duplicadas = [c for c in celdas_ocupadas if celdas_ocupadas.count(c) > 1]
        
        if len(celdas_duplicadas) == 0:
            print(" No hay celdas duplicadas asignadas")
        else:
            print(f" ALERTA: Celdas duplicadas encontradas: {celdas_duplicadas}")
        
        print()
        print("=" * 70)
        
        # Conclusión de la prueba
        if exitos == 1 and len(celdas_duplicadas) == 0:
            print(" PRUEBA EXITOSA: La concurrencia está protegida correctamente")
            print("   Solo un operador pudo asignar la celda, el otro fue rechazado.")
            print("   No hay asignaciones duplicadas en la base de datos.")
            print("   El bloqueo FOR UPDATE (vía with_for_update()) funcionó correctamente.")
        elif exitos == 2:
            print(" PRUEBA CON OBSERVACIONES:")
            print("   Ambos operadores obtuvieron celda. Esto puede deberse a:")
            print("   - Hay más de 1 celda disponible de tipo Automóvil")
            print("   - Los vehículos son de tipos diferentes")
            print("   Ejecuta el script SQL para dejar solo 1 celda disponible.")
        else:
            print(" PRUEBA CON OBSERVACIONES: Revisar implementación")
        
        print("=" * 70)


if __name__ == "__main__":
    ejecutar_prueba_concurrencia()