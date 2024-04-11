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


@app.route('/profile')
@cross_origin()
@jwt_required()
def my_profile():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()  
            
        response_body = {
            "name": user.name,
            "email": user.email,
            "about": user.about,
        }
        return response_body
    except Exception as e:
        return {"msg": str(e)}, 401


