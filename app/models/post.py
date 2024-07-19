from app import db
from datetime import datetime as dt

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    guest_author = db.Column(db.String(80), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    last_update = db.Column(db.DateTime, nullable=True, default=None)
    comments = db.relationship("Comment", backref="post")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
from .user import User
from .comment import Comment