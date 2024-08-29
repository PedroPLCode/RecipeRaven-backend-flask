from app import db
from flask_login import UserMixin
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    login = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(80), unique=False, nullable=True)
    google_user = db.Column(db.Boolean, nullable=False, default=False)
    original_google_picture = db.Column(db.Boolean, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
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
    post_likes = db.relationship('PostLikeIt', backref='user', lazy='dynamic')
    comment_likes = db.relationship('CommentLikeIt', backref='user', lazy='dynamic')
    news_likes = db.relationship('NewsLikeIt', backref='user', lazy='dynamic')
    reactions_likes = db.relationship('ReactionLikeIt', backref='user', lazy='dynamic')
    post_hates = db.relationship('PostHateIt', backref='user', lazy='dynamic')
    comment_hates = db.relationship('CommentHateIt', backref='user', lazy='dynamic')
    news_hates = db.relationship('NewsHateIt', backref='user', lazy='dynamic')
    reactions_hates = db.relationship('ReactionHateIt', backref='user', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)
    
from .post import Post
from .comment import Comment
from .favorite import Favorite
from .news import News
from .reactions import Reaction