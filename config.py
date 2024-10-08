import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "remember-to-add-secret-key"
    SQLALCHEMY_DATABASE_URI = (
            os.environ.get('DATABASE_URL') or
            'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOADED_PHOTOS_DEST = os.path.join(os.getcwd(), 'app/static/uploaded_photos')
    ALLOWED_PHOTOS_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    JWT_SECRET_KEY = 'your-secret-key' 
    
class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True