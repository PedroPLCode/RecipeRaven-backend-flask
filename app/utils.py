import random
from app import app, mail, db
from flask_mail import Message
from app.models import User
import os
from datetime import datetime, timedelta

def get_random_topic(array):
    min_val = 0
    max_val = len(array) - 1
    random_index = get_random_int_inclusive(min_val, max_val)
    return array[random_index]


def get_random_int_inclusive(min_val, max_val):
    return random.randint(min_val, max_val)


def item_is_valid(item):
    for key in item.keys():
        if key != 'id' and key != 'data':
            return False
    return True


def send_email(email, subject, body_html):
    message = Message(subject=subject, recipients=[email])
    message.html = body_html
    try:
        mail.send(message)
        return 'email sent.'
    except Exception as e:
        return str(e)
    
    
def check_and_delete_unconfirmed_users():
    now = datetime.utcnow()
    cutoff_time = now - timedelta(hours=24)

    unconfirmed_users = User.query.filter(User.email_confirmed == False, User.creation_date < cutoff_time).all()

    for user in unconfirmed_users:
        try:
            if user.picture:
                filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], user.picture)
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            db.session.delete(user)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Error deleting user {user.id}: {str(e)}") 