from app import db
from datetime import datetime as dt
        
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    guest_author = db.Column(db.String(80), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    last_update = db.Column(db.DateTime, nullable=True, default=None)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('CommentLikeIt', backref='comment', lazy='dynamic')
    hates = db.relationship('CommentHateIt', backref='comment', lazy='dynamic')
    
class CommentLikeIt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=dt.utcnow)
    
class CommentHateIt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=dt.utcnow)
    
from .user import User
from .post import Post