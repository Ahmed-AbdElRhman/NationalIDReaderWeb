import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file if it exists
# conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=test;DATABASE=test;UID=user;PWD=password')
class Config:
    SECRET_KEY = os.getenv('SUBSCRIPTION_SECRET_KEY', secrets.token_hex(32))
    # SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc:///?odbc_connect= {os.environ.get("DATABASE_URL","DRIVER={SQL Server};SERVER=DESKTOP-TRPSBPE\SQLEXPRESS;DATABASE=OCRDB_dev;")}'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///OCRDB_dev.db'
    ADMIN_USERNAME = 'OCRadmin'
    ADMIN_PASSWORD = 'admin' 
    MAX_SCANS = 100 # Maximum scans allowed per subscription
    SUBSCRIPTION_DAYS = 365 # Subscription duration in days
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}