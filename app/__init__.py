from flask import Flask
from flask_mail import Mail
from flask.cli import load_dotenv
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta
from flask_jwt_extended import JWTManager
from flask_uploads import UploadSet, configure_uploads, IMAGES
import os
from itsdangerous import URLSafeTimedSerializer, BadSignature
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename="repipe_raven.log"
                    )
logging.info('starting app')

app = Flask(__name__, static_folder='static')

load_dotenv()  

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_SECRET_KEY = os.environ['GOOGLE_SECRET_KEY']
GMAIL_APP_PASSWORD = os.environ['GMAIL_APP_PASSWORD']

app.config.from_object(Config)
app.config['SECRET_KEY'] = 'secret_key_here'  # Klucz tajny do podpisu tokena, lepiej przechowywać w konfiguracji aplikacji
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'piotrek.gaszczynski@gmail.com'
app.config['MAIL_PASSWORD'] = GMAIL_APP_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = 'piotrek.gaszczynski@gmail.com'

mail = Mail(app)

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

app.secret_key = b'my-super-top-secret-key'

#app.config['JWT_TOKEN_LOCATION'] = ['cookies'] # NOT SURE?
#jwt_token = request.cookies.get('access_token_cookie') # Demonstration how to get the cookie

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, resources={
    r"/api/*": {"origins": "*"},
}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], supports_credentials=True)

from app.routes import routes as routes_blueprint
app.register_blueprint(routes_blueprint, url_prefix='/')

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": app.models.User,
        "Favorite": app.models.Favorite,
        "Post": app.models.Post,
        "Comment": app.models.Comment,
        "Note": app.models.Note,
    }

from app.routes import main, session, users, rapidapi, posts, comments, favorites, notes
from app.models import User, Post, Comment, Favorite, Note

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)