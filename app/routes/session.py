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

    
@app.route('/token', methods=["POST"])
@cross_origin()
def create_token():
    login = request.json.get("login", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(login = login).first_or_404()
    
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