from app import app, db
from app.models import User, Favorite
from app.utils import *
from werkzeug.utils import secure_filename
import os
from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime as dt
from flask_jwt_extended import get_jwt_identity, jwt_required

@app.route('/api/logins', methods=["GET"])
@cross_origin()
def check_user_login():
    try:
        login_query = request.args.get("login", "")
        if len(login_query) > 0:
            user = User.query.filter_by(login=login_query).first()
            if user:
                user.last_login = dt.utcnow()
                return jsonify({"login_status": True, "message": "Login successful"}), 200
            else:
                return jsonify({"login_status": False, "message": "Login unsuccessful"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
    
    
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
                "email": user.email,
                "name": user.name,
                "about": user.about,
                "picture": user.picture,
                "last_login": user.last_login,
                "last_api_activity": dt.utcnow(),
                "creation_date": user.creation_date,
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
            filename = secure_filename(picture.filename)
            filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
            picture.save(filepath)

        new_user = User(login=login,
                        password=password,
                        email=email,
                        name=name if name else '',
                        about=about if about else '',
                        picture=filename if filename else '',
                        )
        db.session.add(new_user)
        db.session.commit()
        
        response = {"msg": "User created successfully"}
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
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
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
        
        for favorite in user_favorites:
            db.session.delete(favorite)
        db.session.delete(user)
        db.session.commit()
        
        response_body = {
            "name": user.name,
            "email": user.email,
            "about": user.about,
        }
        return response_body, 200
    except Exception as e:
        return {"msg": str(e)}, 401