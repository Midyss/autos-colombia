import mysql.connector
from mysql.connector import Error

def conectar_bd():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='admin',          # O 'root' si usas root
            password='autos123',   # TU CONTRASEÑA DE MYSQL
            database='autos_colombia'
        )
        if conexion.is_connected():
            print(" Conexión exitosa a MySQL")
            return conexion
    except Error as e:
        print(f"Error al conectar: {e}")
        return None