from app import app, db, mail, serializer
from flask_mail import Message
from app.models import User, Favorite, Note
from app.utils import *
from werkzeug.utils import secure_filename
import os
from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime as dt
from flask_jwt_extended import get_jwt_identity, jwt_required
from itsdangerous import URLSafeTimedSerializer, BadSignature
from pathlib import Path
from app.emails_templates import CREATE_USER_EMAIL_BODY, CONFIRM_EMAIL_EMAIL_BODY, DELETE_USER_EMAIL_BODY, RESET_PASSWORD_EMAIL_BODY, PASSWORD_CHANGED_EMAIL_BODY

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

        return jsonify({"message": "No query parameter provided"}), 400

    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
    
    
@app.route('/api/users', methods=["GET"])
@cross_origin()
@jwt_required()
def get_user():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()  
        
        creation_date_str = str(user.creation_date) if user.creation_date else None
        try:
            creation_date_obj = dt.strptime(creation_date_str, "%Y-%m-%d %H:%M:%S.%f") if creation_date_str else None
        except ValueError:
            creation_date_obj = dt.strptime(creation_date_str, "%Y-%m-%d %H:%M:%S") if creation_date_str else None
        formatted_creation_date = creation_date_obj.strftime("%Y-%m-%d %H:%M:%S CET") if creation_date_obj else None
                
        last_login_str = str(user.last_login) if user.last_login else None
        try:
            last_login_obj = dt.strptime(last_login_str, "%Y-%m-%d %H:%M:%S.%f") if last_login_str else None
        except ValueError:
            last_login_obj = dt.strptime(last_login_str, "%Y-%m-%d %H:%M:%S") if last_login_str else None
        formatted_last_login = last_login_obj.strftime("%Y-%m-%d %H:%M:%S CET") if last_login_obj else None
                
        last_activity_str = str(dt.utcnow())
        try:
            last_activity_obj = dt.strptime(last_activity_str, "%Y-%m-%d %H:%M:%S.%f") if last_activity_str else None
        except ValueError:
            last_activity_obj = dt.strptime(last_activity_str, "%Y-%m-%d %H:%M:%S") if last_activity_str else None
        formatted_last_activity = last_activity_obj.strftime("%Y-%m-%d %H:%M:%S CET") if last_activity_obj else None
        
        if user:            
            user_data = {
                "id": user.id,
                "login": user.login,
                "google_user": user.google_user,
                "original_google_picture": user.original_google_picture,
                "email": user.email,
                "name": user.name,
                "about": user.about,
                "picture": user.picture,
                "creation_date": formatted_creation_date,
                "last_login": formatted_last_login,
                "last_api_activity": formatted_last_activity,
                "favorites_count": len(user.favorites),
                "posts_count": len(user.posts),
                "comments_count": len(user.comments),
            }
            return {"user_data": user_data}, 200
        else:
            return {"msg": "User not found"}, 404
        
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
            return {"msg": "Password is required"}, 400

        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()

        passwd_check = user.verify_password(password) if user else False
        return {"passwd_check": passwd_check}, 200
        
    except Exception as e:
        return {"msg": str(e)}, 500

    
@app.route('/api/users', methods=["POST"])
@cross_origin()
def create_user():
    try:
        data = request.form.to_dict()
        login = data.get("login")
        password = data.get("password")
        email = data.get("email")
        name = data.get("name")
        about = data.get("about")
        
        if login is None or password is None:
            return jsonify({"msg": "Wrong email or password"}), 401

        if User.query.filter_by(login=login).first() or User.query.filter_by(email=email).first():
            return jsonify({'message': 'Login or email already exists'}), 400
        
        picture = request.files.get('picture')
        filename = None
        if picture:
            
            path = Path(picture.filename)
            extension = path.suffix
            
            filename = f'{login}{extension}' # if login else secure_filename(picture.filename)
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
        
        token = serializer.dumps(email, salt='confirm-email')
        confirm_url = f'http://127.0.0.1:3000/userconfirmed/{token}'
        email_subject = 'RecipeRavenApp email confirm'
        email_body = CONFIRM_EMAIL_EMAIL_BODY.format(username=name.title() if name else login, link=confirm_url)
        send_email(email, email_subject, email_body)
        return jsonify({"reset_url": confirm_url}), 200
            
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
    
@app.route('/api/users/resend_confirm', methods=["POST"])
@cross_origin()
def create_user():
    try:
        data = request.form.to_dict()
        email = data.get("email")
        
        if email is None:
            return jsonify({"msg": "email not provided"}), 401
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if user.email_confirmed:
                return jsonify({'message': 'User email already confirmed'}), 400
            else:
                token = serializer.dumps(email, salt='confirm-email')
                confirm_url = f'http://127.0.0.1:3000/userconfirmed/{token}'
                email_subject = 'RecipeRavenApp email confirm'
                email_body = CONFIRM_EMAIL_EMAIL_BODY.format(username=user.name.title() if user.name else user.login, link=confirm_url)
                send_email(email, email_subject, email_body)
                return jsonify({"reset_url": confirm_url}), 200
        else:
            return jsonify({"msg": "user not found"}), 401
                
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
    
@app.route('/api/user/confirm/<token>', methods=["POST"])
@cross_origin()
def confirm_user_email(token):
    try:
        email = serializer.loads(token, salt='confirm-email', max_age=3600)
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "User with this token not found"}), 404

        user.email_confirmed = True
        db.session.commit()
            
        email_subject = 'Recipe Raven App welcome'
        email_body = CREATE_USER_EMAIL_BODY.format(username=user.name.title() if user.name else user.login)
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
        if file:
            try:    
    
                path = Path(file.filename)
                extension = path.suffix
                
                filename = user.picture if user.picture else f'{user.login}{extension}' # secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                file.save(filepath)
                data['picture'] = filename
            except Exception as e:
                return jsonify({"msg": f"Error saving file: {str(e)}"}), 500

        if 'picture' in data:
            user.picture = data['picture']

        old_password = data.get("oldPassword")
        new_password = data.get("newPassword")
        if old_password and new_password:
            if user.verify_password(old_password):
                user.password = new_password
                
                email_subject = 'passwd changed'
                email_body = f'Hello {user.name.title()}. passwd changed.'
                send_email(user.email, email_subject, email_body)
        
            else:
                return jsonify({"msg": "Old password is incorrect"}), 400

        user.email = data.get('email', user.email)
        user.name = data.get('name', user.name)
        user.about = data.get('about', user.about)

        db.session.commit()

        return jsonify({"msg": "User details updated successfully"}), 200

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
            os.remove(filepath) ### NOT SURE WILL WORK
        
        for favorite in user_favorites:
            try:
                if 'image_name' in favorite.data:
                    image_name = favorite.data['image_name']
                    image_to_delete = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], image_name)
                    
                    if os.path.exists(image_to_delete):
                        os.remove(image_to_delete)
                        print(f"File Deleted: {image_to_delete}")
                    else:
                        print(f"File Not Exists: {image_to_delete}")
                        
                note = Note.query.filter_by(favorite_id=favorite.id).first()
                if note:
                    db.session.delete(note)

                db.session.delete(favorite)
                
            except Exception as e:
                db.session.rollback()
                return {"msg": f"An error occurred during deletion: {str(e)}"}, 500

        db.session.delete(user)
        db.session.commit()
        
        response_body = {
            "name": user.name,
            "email": user.email,
            "about": user.about,
        }
        
        email_subject = 'Bye bye FoodApp test'
        email_body = DELETE_USER_EMAIL_BODY.format(username=user.name.title() if user.name else user.login)
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
                email_subject = 'RecipeRavenApp password reset'
                email_body = RESET_PASSWORD_EMAIL_BODY.format(username=user.name.title() if user.name else user.login, link=reset_url)
                send_email(email_address, email_subject, email_body)
                return jsonify({"reset_url": reset_url}), 200
            else:
                return jsonify({"msg": "User not found"}), 400
        else:
            return jsonify({"msg": "Email address not provided"}), 400

    except Exception as e:
        return jsonify({"msg": str(e)}), 500


@app.route('/api/resetpassword/reset/<token>', methods=["POST"])
def reset_password(token):
    try:
        new_password = request.json.get('new_password')

        if not new_password:
            return jsonify({"error": "Missing data - no new password"}), 400

        email = serializer.loads(token, salt='reset-password', max_age=3600)
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "User with this token not found"}), 404

        user.password = new_password
        db.session.commit()
        
        email_subject = 'RecipeRavenApp password changed'
        email_body = PASSWORD_CHANGED_EMAIL_BODY.format(username=user.name.title() if user.name else user.login)
        send_email(user.email, email_subject, email_body)

        return jsonify({"message": "success. password was changed"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500