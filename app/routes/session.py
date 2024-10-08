from app import GOOGLE_CLIENT_ID, GOOGLE_SECRET_KEY, app, db
from app.utils import *
from app.routes import limiter
from flask import jsonify, request
from datetime import datetime as dt
from flask_cors import cross_origin
from datetime import datetime, timedelta, timezone
from app.models import User
import json
import requests
import logging
from pathlib import Path
from app.emails_templates import CREATE_USER_EMAIL_BODY
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required

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
@limiter.limit("5 per minute")
def create_token():
    login = request.json.get("login", None)
    password = request.json.get("password", None)
    
    if not login or not password:
        return jsonify({"msg": "Missing login or password."}), 401
    
    user = User.query.filter_by(login = login).first()
    
    if user and user.verify_password(password):
        if user.email_confirmed:
            access_token = create_access_token(identity=login)
            response = {"msg": "Logged in succesfully",
                        "access_token": access_token, 
                        'email_confirmed': user.email_confirmed}
            user.last_login = dt.utcnow()
            logging.info(f'User {user.login} logged in.')
            db.session.commit()
            return response
        else:
            response = {"msg": "Email not confirmed",
                        "access_token": True,
                        "email_confirmed": user.email_confirmed}
            return response
    else:
        logging.warn(f'Someone trying to login. Invalid password.')
        return jsonify({"msg": "Wrong login or password."}), 401


@app.route('/google_token', methods=['POST'])
@cross_origin()
def create_google_token():
    auth_code = request.get_json().get('code')
    
    if not auth_code:
        return jsonify({"msg": "Authorization code is missing."}), 400

    data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID, 
        'client_secret': GOOGLE_SECRET_KEY,
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.post('https://oauth2.googleapis.com/token', data=data)
        response.raise_for_status()
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"msg": str(e)}), 500

    headers = {
        'Authorization': f'Bearer {response_data["access_token"]}'
    }

    try:
        google_user_info = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo', 
            headers=headers
        ).json()
    except requests.exceptions.RequestException as e:
        return jsonify({"msg": str(e)}), 500
    
    google_login = google_user_info['email']
    user = User.query.filter_by(login=google_login).first() or User.query.filter_by(email=google_login).first()
    response_msg = False
    
    if not user: 
        try:
            picture_url = google_user_info.get('picture')
            if picture_url:
                picture_response = requests.get(picture_url)
                if picture_response.status_code == 200:
                    extension = Path(picture_url).suffix
                    filename = f'{google_login}{extension}'
                    filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
                    with open(filepath, 'wb') as f:
                        f.write(picture_response.content)
            
            new_google_user = User(
                login=google_user_info.get('email'),
                google_user=True,
                email=google_user_info.get('email'),
                email_confirmed=True,
                name=google_user_info.get('given_name', ''),
                about=google_user_info.get('name', ''),
                last_login=dt.utcnow(),
                picture=filename if filename else '',
                original_google_picture=False
            )
            db.session.add(new_google_user)
            db.session.commit()
            user = new_google_user
            logging.info(f'User {user.login} created.')
            
            email_subject = 'Welcome in RecipeRavenApp.'
            email_body = CREATE_USER_EMAIL_BODY.format(
                username=new_google_user.name.title()
                )
            send_email(new_google_user.email, email_subject, email_body)
            
            response_msg = 'Google User created and logged in succesfully.'
    
        except Exception as e:
            return jsonify({"msg": str(e)}), 500
    else:
        if user.google_user:
            logging.info(f'User {user.login} logged in.')
            user.last_login = dt.utcnow()
            db.session.commit()
            response_msg = 'Google User logged in succesfully.'
        else:
            return jsonify({'msg': 'GoogleO2Auth. Login or email already exists.'}), 400

    access_token = create_access_token(identity=google_login)
    response = {"access_token": access_token,
                "msg": response_msg,
                }
        
    return jsonify(response), 200


@app.route("/logout", methods=["POST"])
@cross_origin()
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    response = jsonify({"msg": "Logout successful."})
    unset_jwt_cookies(response)
    logging.info(f'User {current_user} logged out.')
    return response