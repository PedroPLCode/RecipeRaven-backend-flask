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
        return False
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d %H:%M:%S CET")
        except ValueError:
            continue
    return False
    
    
def get_author_info(user):
    return {
        'author': user.name or user.login if user else False,
        'author_picture': user.picture if user else False,
        'author_google_user': user.google_user if user else False,
        'author_original_google_picture': user.original_google_picture if user else False
    }
    

def format_post_news_dates(creation_date, last_update):
    return {
        'creation_date': format_date(str(creation_date)),
        'last_update': format_date(str(last_update))
    }
    
    
def process_post_news(item):
    user_info = get_author_info(item.user)
    dates = format_post_news_dates(item.creation_date, item.last_update)
    
    result = {
        'id': item.id,
        'user_id': item.user_id,
        'content': item.content,
        'title': item.title,
        **user_info,
        **dates,
        'likes': [like.user_id for like in item.likes],
        'hates': [hate.user_id for hate in item.hates],
    }

    if hasattr(item, 'guest_author'):
            result['guest_author'] = item.guest_author or False
        
    if hasattr(item, 'comments'):
        result['comments'] = [process_comments_reaction(comment) for comment in item.comments]
        
    if hasattr(item, 'reactions'):
        result['reactions'] = [process_comments_reaction(reaction) for reaction in item.reactions]

    return result
    
    
def process_comments_reaction(item):
    
    result =  {
        'id': item.id,
        'user_id': item.user_id,
        'content': item.content,
        'author': item.user.name or item.user.login if item.user else False,
        'guest_author': item.guest_author if item.guest_author else False,
        'creation_date': format_date(str(item.creation_date)),
        'last_update': format_date(str(item.last_update)),
    }
    
    if item.likes:
        result['likes'] = [like.user_id for like in item.likes],
        
    if item.hates:
        result['hates'] = [hate.user_id for hate in item.hates],
    
    return result
    
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