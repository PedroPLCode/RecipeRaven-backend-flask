from app import db
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    login = db.Column(db.String(80), unique=True, nullable=False)
    google_user = db.Column(db.Boolean, nullable=False)
    original_google_picture = db.Column(db.Boolean, nullable=True)
    password_hash = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=True)
    about = db.Column(db.String(80), nullable=True)
    picture = db.Column(db.String(80), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    last_login = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    favorites = db.relationship("Favorite", backref="user")
    posts = db.relationship("Post", backref="user")
    comments = db.relationship("Comment", backref="user")
    news = db.relationship("News", backref="user")
    reactions = db.relationship("Reaction", backref="user")
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
from .post import Post
from .comment import Comment
from .favorite import Favorite
from .news import News
from .reactions import Reaction