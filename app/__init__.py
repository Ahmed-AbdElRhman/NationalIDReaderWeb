from flask import Flask
from dotenv import load_dotenv
load_dotenv()
from .config import Config
from app.utils.logging_config import setup_logging
def create_app(config_class=Config):
    app = Flask(__name__,template_folder='Front/templates', static_folder='Front/static')
    app.config.from_object(config_class)
    
    # Initialize extensions
    # register_extensions(app)
    # Register blueprints
    # register_blueprints(app)
    
    # Configure logging  
    setup_logging(app)
    
    return app

# def register_extensions(app):
#     db.init_app(app)

def register_blueprints(app):
    from app.Routes.IDReaderEndPoints import IDReaderEndPoints    
    app.register_blueprint(IDReaderEndPoints)
    # Register other blueprints here as needed