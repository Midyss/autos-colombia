import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-123')
    
    # Aquí configuramos la conexión con los datos :
    # Formato: mysql+pymysql://USUARIO:CONTRASEÑA@localhost/NOMBRE_BD
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:autos123@localhost/autos_colombia'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False