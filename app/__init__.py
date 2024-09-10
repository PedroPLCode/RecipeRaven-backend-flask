from flask import Flask
from flask_admin import Admin
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
from itsdangerous import URLSafeTimedSerializer
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename="repipe_raven.log"
                    )
logging.info('Receipe Raven App starting.')

def create_app(config_name=None):
    app = Flask(__name__, static_folder='static')
    if config_name:
        app.config.from_object(config_name)
        db.init_app(app)
        jwt.init_app(app)
        with app.app_context():
            from app.routes import routes as routes_blueprint
            app.register_blueprint(routes_blueprint, url_prefix='/')
            from app.routes import session
            db.create_all()
    return app

app = create_app()

load_dotenv()  

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_SECRET_KEY = os.environ['GOOGLE_SECRET_KEY']
GMAIL_APP_PASSWORD = os.environ['GMAIL_APP_PASSWORD']

app.config.from_object(Config)
app.config['SECRET_KEY'] = 'secret_key_here' 
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.config['SESSION_PERMANENT'] = False

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

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, resources={
    r"/api/*": {"origins": "*"},
}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], supports_credentials=True)

admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')

from app.routes import routes as routes_blueprint
app.register_blueprint(routes_blueprint, url_prefix='/')

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": app.models.User,
        "Favorite": app.models.Favorite,
        "Note": app.models.Note,
        "Post": app.models.Post,
        "PostLikeIt": app.models.PostLikeIt,
        "PostHateIt": app.models.PostHateIt,
        "Comment": app.models.Comment,
        "CommentLikeIt": app.models.CommentLikeIt,
        "CommentHateIt": app.models.CommentHateIt,
        "News": app.models.News,
        "NewsLikeIt": app.models.NewsLikeIt,
        "NewsHateIt": app.models.NewsHateIt,
        "Reaction": app.models.Reaction,
        "ReactionLikeIt": app.models.ReactionLikeIt,
        "ReactionHateIt": app.models.ReactionHateIt,
        "Newsletter": app.models.Newsletter,
    }

from app.routes import (main, 
                        session, 
                        users, 
                        rapidapi, 
                        posts, 
                        comments, 
                        favorites, 
                        notes, 
                        news, 
                        reactions, 
                        admin,
                        )
from app.models import (User,
                        Post, 
                        PostLikeIt, 
                        PostHateIt, 
                        Comment, 
                        CommentLikeIt, 
                        CommentHateIt, 
                        Favorite, 
                        Note, 
                        News, 
                        NewsLikeIt, 
                        NewsHateIt, 
                        Reaction, 
                        ReactionLikeIt, 
                        ReactionHateIt, 
                        Newsletter,
                        )
from app.models.admin import (UserAdmin, 
                              FavoriteAdmin, 
                              NoteAdmin, 
                              PostAdmin, 
                              PostLikeItAdmin, 
                              PostHateItAdmin, 
                              CommentAdmin, 
                              CommentLikeItAdmin, 
                              CommentHateItAdmin, 
                              NewsAdmin, 
                              NewsLikeItAdmin, 
                              NewsHateItAdmin, 
                              ReactionAdmin, 
                              ReactionLikeItAdmin, 
                              ReactionHateItAdmin, 
                              NewsletterAdmin
                              )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)