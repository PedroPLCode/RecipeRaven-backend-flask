from app import db
from datetime import datetime as dt

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    last_update = db.Column(db.DateTime, nullable=True, default=None)
    reactions = db.relationship("Reaction", backref="news")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('NewsLikeIt', backref='news', lazy='dynamic')
    hates = db.relationship('NewsHateIt', backref='news', lazy='dynamic')
    
class NewsLikeIt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=dt.utcnow)
    
class NewsHateIt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=dt.utcnow)
    
from .user import User
from .reactions import Reaction