import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "remember-to-add-secret-key"
    SQLALCHEMY_DATABASE_URI = (
            os.environ.get('DATABASE_URL') or
            'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOADED_PHOTOS_DEST = os.path.join(os.getcwd(), 'app/static/profile_pictures')  # folder, w którym będą przechowywane zdjęcia
    ALLOWED_PHOTOS_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    admin_id = 1