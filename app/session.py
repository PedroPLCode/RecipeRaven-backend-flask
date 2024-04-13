from app import app, db
from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime, timedelta, timezone
from app.models import User, Post, Comment, Favorite
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
import json
from PRIVATE_API_KEY import PRIVATE_API_KEY

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        return response
    
    
@app.route('/user', methods=["GET"])
@cross_origin()
@jwt_required()
def get_user():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()  
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
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/user', methods=["POST"])
@cross_origin()
def create_user():
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


@app.route('/user', methods=["DELETE"])
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

    
@app.route('/token', methods=["POST"])
@cross_origin()
def create_token():
    login = request.json.get("login", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(login = login).first()
    
    if user and user.verify_password(password):
        access_token = create_access_token(identity=login)
        response = {"access_token": access_token}
        return response
    else:
        return {"msg": "Wrong email or password"}, 401


@app.route("/logout", methods=["POST"])
@cross_origin()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response