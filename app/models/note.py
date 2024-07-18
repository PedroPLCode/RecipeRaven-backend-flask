from app import db
from datetime import datetime as dt

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
        
from .favorite import Favorite