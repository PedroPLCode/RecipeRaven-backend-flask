import random
from app import mail, app, db
from flask_mail import Message
from app.models import User
import os

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
    all_users = User.query.all()  
    
    for user in all_users:
        
        if user.email_confirmed==False and user.creation_date==OLDER_THAN_24hrs:
            
            try: 
                
                filename = user.picture if user.picture else None
                filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename) if filename else None
                if os.path.exists(filepath):
                    os.remove(filepath) ### NOT SURE WILL WORK
                    
                db.session.delete(user)
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()