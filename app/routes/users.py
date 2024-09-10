from app import app, db, serializer
from app.models import User, Favorite, Note
from app.utils import *
from app.routes import limiter
import os
import logging
from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime as dt
from flask_jwt_extended import get_jwt_identity, jwt_required
from pathlib import Path
from app.emails_templates import (CREATE_USER_EMAIL_BODY, 
                                  CONFIRM_EMAIL_EMAIL_BODY, 
                                  DELETE_USER_EMAIL_BODY, 
                                  RESET_PASSWORD_EMAIL_BODY, 
                                  PASSWORD_CHANGED_EMAIL_BODY
                                  )

@app.route('/api/check_user/', methods=["GET"])
@cross_origin()
def check_user():
    try:
        login_query = request.args.get("login", "")
        email_query = request.args.get("email", "")

        if login_query:
            user = User.query.filter_by(login=login_query).first()
            return jsonify({"login_status": bool(user)}), 200

        if email_query:
            user = User.query.filter_by(email=email_query).first()
            return jsonify({"email_status": bool(user)}), 200

        return jsonify({"msg": "No query parameter provided."}), 400

    except Exception as e:
        return jsonify({"msg": "An error occurred.", "error": str(e)}), 500
    
    
@app.route('/api/users', methods=["GET"])
@cross_origin()
@jwt_required()
def get_user():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()  
        
        if user:            
            user_data = {
                "id": user.id,
                "login": user.login,
                "google_user": user.google_user,
                "original_google_picture": user.original_google_picture,
                "email": user.email,
                "email_confirmed": user.email_confirmed,
                "name": user.name,
                "about": user.about,
                "picture": user.picture,
                "creation_date": format_date(str(user.creation_date)),
                "last_login": format_date(str(user.last_login)),
                "last_api_activity": format_date(str(str(dt.utcnow()))),
                "favorites_count": len(user.favorites),
                "posts_count": len(user.posts),
                "comments_count": len(user.comments),
            }
            return {"user_data": user_data}, 200
        else:
            return {"msg": "User not found."}, 404
        
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/api/userpasswdcheck', methods=["POST"])
@cross_origin()
@jwt_required()
def check_user_password():
    try:
        data = request.form.to_dict() or request.json
        password = data.get("password")

        if not password:
            return {"msg": "Password is required."}, 400

        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()

        passwd_check = user.verify_password(password) if user else False
        return {"passwd_check": passwd_check}, 200
        
    except Exception as e:
        return {"msg": str(e)}, 500

    
@app.route('/api/users', methods=["POST"])
@cross_origin()
@limiter.limit("5 per minute")
def create_user():
    try:
        data = request.form.to_dict()
        login = data.get("login")
        password = data.get("password")
        email = data.get("email")
        name = data.get("name")
        about = data.get("about")
        
        if login is None or password is None:
            return jsonify({"msg": "Wrong email or password."}), 401

        if User.query.filter_by(login=login).first() or User.query.filter_by(email=email).first():
            return jsonify({'msg': 'Login or email already exists.'}), 400
        
        picture = request.files.get('picture')
        filename = None
        if picture:
            path = Path(picture.filename)
            extension = path.suffix
            filename = f'{login}{extension}'
            filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
            picture.save(filepath)

        new_user = User(login=login,
                        google_user = False,
                        password=password,
                        email=email,
                        email_confirmed=False,
                        name=name if name else '',
                        about=about if about else '',
                        picture=filename if filename else '',
                        )
        db.session.add(new_user)
        db.session.commit()
        logging.info(f'User {new_user.login} created.')
        
        token = serializer.dumps(email, salt='confirm-email')
        confirm_url = f'http://127.0.0.1:3000/user/confirm/{token}'
        email_subject = 'Confirm Your email address.'
        email_body = CONFIRM_EMAIL_EMAIL_BODY.format(
            username=name.title() if name else login, link=confirm_url
            )
        send_email(email, email_subject, email_body)
        
        return jsonify({"msg": 'User created. Check your email.'}), 200
            
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    

@app.route('/api/resend/', methods=["POST"])
@cross_origin()
def reconfirm_user():
    try:
        data = request.form.to_dict()
        email = data.get("email")

        if not email:
            return jsonify({"msg": "No email provided."}), 400

        user = User.query.filter_by(email=email, google_user=False).first_or_404()

        if not user.email_confirmed:
            token = serializer.dumps(email, salt='confirm-email')
            confirm_url = f'http://127.0.0.1:3000/user/confirm/{token}'
            email_subject = 'Confirm Your email address.'
            email_body = CONFIRM_EMAIL_EMAIL_BODY.format(
                username=user.name.title() if user.name else user.name,
                link=confirm_url
            )
            send_email(user.email, email_subject, email_body)
            return jsonify({"msg": 'Email send. Check your email.'}), 200
        else:
            return jsonify({'msg': 'Email already confirmed.'}), 200

    except Exception as e:
        return jsonify({"msg": "An error occurred. Please try again later."}), 500
    
    
@app.route('/api/user/confirm/<token>', methods=["POST"])
@cross_origin()
def confirm_user_email(token):
    try:
        email = serializer.loads(token, salt='confirm-email', max_age=3600)
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"msg": "User with this token not found."}), 404

        user.email_confirmed = True
        logging.info(f'User {user.login} email confirmed.')
        db.session.commit()
            
        email_subject = 'Welcome in Recipe Raven App.'
        email_body = CREATE_USER_EMAIL_BODY.format(
            username=user.name.title() if user.name else user.login
            )
        send_email(user.email, email_subject, email_body)
        
        response = {"msg": "User email confirmed successfully"}
        return jsonify(response), 201 
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

    
@app.route('/api/users', methods=["PUT"])
@cross_origin()
@jwt_required()
def change_user():
    try:
        current_user_login = get_jwt_identity()
        user = User.query.filter_by(login=current_user_login).first_or_404()
        data = request.form.to_dict()
        file = request.files.get('picture')
        
        if not user:
            return jsonify({"msg": "Error. User not found."}), 400        
        
        if file:
            try:    
                path = Path(file.filename)
                extension = path.suffix
                filename = user.picture if user.picture else f'{user.login}{extension}'
                filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                         
                file.save(filepath)
                data['picture'] = filename
                logging.info(f'User {user.login} picture changed.')
                return jsonify({"msg": "Picture changed"}), 201
            except Exception as e:
                return jsonify({"msg": f"Error saving file: {str(e)}"}), 500

        if 'picture' in data:
            user.picture = data['picture']

        old_password = data.get("oldPassword")
        new_password = data.get("newPassword")
        if old_password and new_password:
            if user.verify_password(old_password):
                user.password = new_password
                logging.info(f'User {user.login} password changed.')
                email_subject = 'Your Password has been changed.'
                email_body = PASSWORD_CHANGED_EMAIL_BODY.format(
                    username=user.name.title() if user.name else user.login
                    )
                send_email(user.email, email_subject, email_body)
                return jsonify({"msg": "Password changed"}), 201
            else:
                return jsonify({"msg": "Old password is incorrect"}), 400

        user.email = data.get('email', user.email)
        user.name = data.get('name', user.name)
        user.about = data.get('about', user.about)
        db.session.commit()
        logging.info(f'User {user.login} details changed.')

        return jsonify({"msg": "User details updated successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 400


@app.route('/api/users', methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_user():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()  
        user_favorites = Favorite.query.filter_by(user_id=user.id).all()
        filename = user.picture if user.picture else None
        filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename) if filename else None
        
        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            pass
        
        for favorite in user_favorites:
            try:
                if 'image_name' in favorite.data:
                    image_name = favorite.data['image_name']
                    image_to_delete = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], image_name)
                    
                    if os.path.exists(image_to_delete):
                        os.remove(image_to_delete)
                    else:
                        pass
                        
                note = Note.query.filter_by(favorite_id=favorite.id).first()
                if note:
                    db.session.delete(note)

                db.session.delete(favorite)
                
            except Exception as e:
                db.session.rollback()
                return {"msg": f"An error occurred during deletion: {str(e)}"}, 500

        db.session.delete(user)
        db.session.commit()
        
        logging.info(f'User {user.login} deleted.')
        
        response_body = {
            "name": user.name,
            "email": user.email,
            "about": user.about,
        }
        
        email_subject = 'Your account has been removed.'
        email_body = DELETE_USER_EMAIL_BODY.format(
            username=user.name.title() if user.name else user.login
            )
        send_email(user.email, email_subject, email_body)
            
        return response_body, 200
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/api/resetpassword', methods=["POST"])
def reset_password_request():
    try:
        data = request.json
        email_address = data.get('email')

        if email_address:
            user = User.query.filter_by(email=email_address).first_or_404()
            if user:
                token = serializer.dumps(email_address, salt='reset-password')
                reset_url = f'http://127.0.0.1:3000/resetpassword/{token}'
                email_subject = 'Reset Your password.'
                email_body = RESET_PASSWORD_EMAIL_BODY.format(
                    username=user.name.title() if user.name else user.login,
                    link=reset_url
                    )
                send_email(email_address, email_subject, email_body)
                
                return jsonify({"reset_url": reset_url}), 200
            else:
                return jsonify({"msg": "User not found."}), 400
        else:
            return jsonify({"msg": "Email address not provided."}), 400

    except Exception as e:
        return jsonify({"msg": str(e)}), 500


@app.route('/api/resetpassword/reset/<token>', methods=["POST"])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='reset-password', max_age=3600)
        user = User.query.filter_by(email=email).first()
        new_password = request.json.get('new_password')

        if not new_password:
            return jsonify({"msg": "Missing data. No new password."}), 400

        if not user:
            return jsonify({"msg": "User with this token not found."}), 404

        user.password = new_password
        db.session.commit()
        
        logging.info(f'User {user.login} password changed.')
        
        email_subject = 'Your Password has been changed.'
        email_body = PASSWORD_CHANGED_EMAIL_BODY.format(
            username=user.name.title() if user.name else user.login
            )
        send_email(user.email, email_subject, email_body)

        return jsonify({"msg": "Password changed succesfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500