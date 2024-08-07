from app import db
from datetime import datetime as dt
        
class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    guest_author = db.Column(db.String(80), nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    last_update = db.Column(db.DateTime, nullable=True, default=None)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('ReactionLikeIt', backref='reaction', lazy='dynamic')
    hates = db.relationship('ReactionHateIt', backref='reaction', lazy='dynamic')
    
class ReactionLikeIt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reaction_id = db.Column(db.Integer, db.ForeignKey('reaction.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=dt.utcnow)
    
class ReactionHateIt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reaction_id = db.Column(db.Integer, db.ForeignKey('reaction.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=dt.utcnow)
    
from .user import User
from .news import News