from app import db
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    login = db.Column(db.String(80), unique=True, nullable=False)
    google_login = db.Column(db.Boolean, nullable=False)
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
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    guest_author = db.Column(db.String(80), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    last_update = db.Column(db.DateTime, nullable=True, default=None)
    comments = db.relationship("Comment", backref="post")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        
        
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    guest_author = db.Column(db.String(80), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    last_update = db.Column(db.DateTime, nullable=True, default=None)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON, nullable=False)
    note = db.relationship("Note", backref="favorite")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data,
            'user_id': self.user_id
        }
    

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    favorite_id = db.Column(db.Integer, db.ForeignKey('favorite.id'))
        
    def to_dict(self):
        return {
            'id': self.id,
            'favorite_id': self.favorite_id,
            'content': self.content,
        }