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
    
from .user import User
from .reactions import Reaction