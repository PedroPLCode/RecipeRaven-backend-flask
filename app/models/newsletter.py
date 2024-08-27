from app import db
from datetime import datetime as dt

class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    recipients = db.Column(db.JSON, nullable=False)
    comment = db.Column(db.Text, nullable=True)