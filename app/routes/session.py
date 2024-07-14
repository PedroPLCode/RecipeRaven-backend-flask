from app import GOOGLE_CLIENT_ID, GOOGLE_SECRET_KEY, app, db
from flask import jsonify, request
from datetime import datetime as dt
from flask_cors import cross_origin
from datetime import datetime, timedelta, timezone
from app.models import User
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required
import json
import requests
from dotenv import load_dotenv

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
        user.last_login = dt.utcnow()
        db.session.commit()
        return response
    else:
        return {"msg": "Wrong email or password"}, 401


@app.route('/google_token', methods=['POST'])
def create_google_token():
    auth_code = request.get_json()['code']

    data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID, 
        'client_secret': GOOGLE_SECRET_KEY,
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data).json()
    headers = {
        'Authorization': f'Bearer {response["access_token"]}'
    }
    google_user_info = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers).json()
    
    if not User.query.filter_by(email=google_user_info['email'], google_user=True).first():
        try:
            login = google_user_info("email")
            email = google_user_info("email")
            name = google_user_info("name")
            picture = google_user_info("picture")
            
            new_google_user = User(login=login,
                                google_user=True,
                                email=email,
                                name=name if name else '',
                                last_login = dt.utcnow(),
                                picture=picture if picture else '',
                                )
            db.session.add(new_google_user)
            db.session.commit()
            
        except Exception as e:
            return jsonify({"msg": str(e)}), 500

    #jwt_token = create_access_token(identity=google_user_info['email']) 
    #response = jsonify(user=google_user_info)
    #response.set_cookie('access_token_cookie', value=jwt_token, secure=True)
    access_token = create_access_token(identity=google_user_info("email"))
    response = {"access_token": access_token}
    #user.last_login = dt.utcnow()
    #db.session.commit()
    #return response
    return response, 200


@app.route("/logout", methods=["POST"])
@cross_origin()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response