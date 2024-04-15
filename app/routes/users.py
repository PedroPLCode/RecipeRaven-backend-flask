from app import app, db
from app.models import User, Post, Comment, Favorite
from app.utils import *
#from config import Config
from flask import jsonify, request, render_template
from flask_cors import cross_origin
import json
import requests
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from PRIVATE_API_KEY import PRIVATE_API_KEY

@app.route('/api/users', methods=["GET"])
@cross_origin()
@jwt_required()
def get_user():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()  
        
        if user:
            user_favorites = Favorite.query.filter_by(user_id=user.id).all()
            user_posts = Post.query.filter_by(user_id=user.id).all()
            user_comments = Comment.query.filter_by(user_id=user.id).all()
            
            response_body = {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "about": user.about,
                "picture": user.picture,
                "creation_date": user.creation_date,
                "last_login": user.last_login,
            }
            return response_body, 200
        else:
            return {"msg": "User not found"}, 404
        
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/api/users', methods=["POST"])
@cross_origin()
def create_user():
    try:
        login = request.json.get("login", None)
        password = request.json.get("password", None)
        email = request.json.get("email", None)
        name = request.json.get("name", None)
        about = request.json.get("about", None)

        if login == None or password == None:
            return {"msg": "Wrong email or password"}, 401

        new_user = User(login=login,
                        password=password,
                        email=email,
                        name=name,
                        about=about,
                        )
        db.session.add(new_user)
        db.session.commit()
        
        response = {"new_user":new_user}
        return response
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/api/users', methods=["PUT"])
@cross_origin()
@jwt_required()
def change_user():
    try:
        current_user_login = get_jwt_identity()
        user = User.query.filter_by(login=current_user_login).first_or_404()
        
        old_password = request.json.get("oldPassword", None)
        new_password = request.json.get("newPassword", None)
        email = request.json.get("email", user.email)
        name = request.json.get("name", user.name)
        about = request.json.get("about", user.about)

        if old_password and new_password:
            if user.verify_password(old_password):
                user.password = new_password
        else:            
            user.email = email
            user.name = name
            user.about = about

        db.session.commit()

        response = {
            "login": user.login,
            "name": user.name,
            "email": user.email,
            "about": user.about,
            "picture": user.picture,
            "creation_date": user.creation_date,
            "last_login": user.last_login,
        }
        
        return response, 200

    except Exception as e:
        return {"msg": str(e)}, 401


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