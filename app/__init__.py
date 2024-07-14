from flask import Flask
from flask.cli import load_dotenv
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta
from flask_jwt_extended import JWTManager
from flask_uploads import UploadSet, configure_uploads, IMAGES
import os

app = Flask(__name__, static_folder='static')

app.config.from_object(Config)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

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

load_dotenv()  

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_SECRET_KEY = os.environ['GOOGLE_SECRET_KEY']


from app.routes import routes as routes_blueprint
app.register_blueprint(routes_blueprint, url_prefix='/')

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": models.User,
        "Favorite": models.Favorite,
        "Post": models.Post,
        "Comment": models.Comment,
        "Note": models.Note,
    }

from app import routes, models
from app.routes import session, favorites, posts, comments, users, rapidapi, notes