from flask import Flask
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta
from flask_jwt_extended import JWTManager

app = Flask(__name__, static_folder='templates')

app.config.from_object(Config)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)
cors = CORS(app, resources={r"/favorites": {"origins": "*"}})

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": models.User,
        "Favorite": models.Favorite,
        "Post": models.Post,
        "Comment": models.Comment,
    }

from app import routes, session, models