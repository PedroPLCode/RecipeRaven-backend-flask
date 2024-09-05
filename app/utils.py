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
        return True
    except Exception as e:
        return str(e)
    

def format_date(date_str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d %H:%M:%S CET")
        except ValueError:
            continue
    return None
    
    
def process_post_news(item):
    return {
        'id': item.id,
        'user_id': item.user_id,
        'content': item.content,
        'title': item.title,
        'author': item.user.name or item.user.login if item.user else None,
        'guest_author': item.guest_author if item.guest_author else None,
        'author_picture': item.user.picture if item.user else None,
        'author_google_user': item.user.google_user if item.user else None,
        'author_original_google_picture': item.user.original_google_picture if item.user else None,
        'creation_date': format_date(str(item.creation_date)),
        'last_update': format_date(str(item.last_update)),
        'comments': [process_comments_reaction(sub_item) for sub_item in item.comments] or None,
        'reactions': [process_comments_reaction(reaction) for reaction in item.reactions] or None,
        'likes': [like.user_id for like in item.likes],
        'hates': [hate.user_id for hate in item.hates],
    }
    
    
def process_comments_reaction(item):
    return {
        'id': item.id,
        'user_id': item.user_id,
        'content': item.content,
        'author': item.user.name or item.user.login if item.user else None,
        'guest_author': item.guest_author if item.guest_author else None,
        'creation_date': format_date(str(item.creation_date)),
        'last_update': format_date(str(item.last_update)),
        'likes': [like.user_id for like in item.likes],
        'hates': [hate.user_id for hate in item.hates],
    }
    
    
def check_and_delete_unconfirmed_users():
    now = datetime.utcnow()
    cutoff_time = now - timedelta(hours=24)
    unconfirmed_users = User.query.filter(User.email_confirmed == False, 
                                          User.creation_date < cutoff_time).all()
    for user in unconfirmed_users:
        try:
            if user.picture:
                filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], 
                                        user.picture)
                if os.path.exists(filepath):
                    os.remove(filepath)
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting user {user.id}: {str(e)}") 