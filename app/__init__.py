from flask import Flask
from app.config import Config
from app.extensions import db
from app.rutas import bp
from flask_cors import CORS

def create_app(config_class=Config):
    # 1. Creamos la aplicación Flask
    app = Flask(__name__, static_folder='../frontend', static_url_path='/static')
    
    # 2. Le cargamos la configuración
    app.config.from_object(config_class)
    
    # 3. Conectamos la base de datos
    db.init_app(app)
    
    # 4. Activamos CORS para permitir peticiones desde el frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 5. Registramos las rutas de la API
    app.register_blueprint(bp)
    
    return app