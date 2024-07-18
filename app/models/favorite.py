from app import db
from datetime import datetime as dt

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
        
from .user import User
from .note import Note