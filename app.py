import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from sqlalchemy import Column, Integer, Text
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os.path
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
                               
# https://hackersandslackers.com/flask-login-user-authentication/
# https://www.geeksforgeeks.org/how-to-add-authentication-to-your-app-with-flask-login/

login_manager = LoginManager()
app = Flask(__name__)
db = SQLAlchemy()
db_name = 'favorites.db'
login_manager.init_app(app)
CORS(app)
cors = CORS(app, resources={r"/favorites": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    name = db.Column(db.String)
    about = db.Column(db.String)
    picture = db.Column(db.String)
    created_on = db.Column(db.String)
    last_login = db.Column(db.String)
    
    def verify_password(self, password):
        pwhash = bcrypt.hashpw(password, self.password)
        return self.password == pwhash


class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON, nullable=False)
    
    
db_url = 'sqlite:///favorites.db'
engine = create_engine(db_url)
Favorite.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
    
favorites = []

nextFavoriteId = 1


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
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email != "pedro" or password != "pedro":
        return {"msg": "Wrong email or password"}, 401
    access_token = create_access_token(identity=email)
    response = {"access_token":access_token}
    return response


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
    response_body = {
        "name": "Pedro",
        "about" :"Details about Pedro"
    }
    return response_body


@app.route('/favorites', methods=['GET'])
@cross_origin()
def get_favorites():
    try:
        dataLoadedFromDB = db.session.execute(db.select(Favorite))
        if not isinstance(favorites, list):
            favorites.append(dataLoadedFromDB)
    except Exception as error:
        return str(error)
    return jsonify(favorites)


def get_favorite(id):
    return next((f for f in favorites if f['id'] == id), None)


def favorite_is_valid(favorite):
    for key in favorite.keys():
        if key != 'id' and key != 'data':
            return False
    return True


@app.route('/favorites', methods=['POST'])
@cross_origin()
def create_favorite():
    global nextFavoriteId
    newFavorite = {}
    newFavorite['data'] = json.loads(request.data)
    newFavorite['id'] = nextFavoriteId
    nextFavoriteId += 1
    if not favorite_is_valid(newFavorite):
        return jsonify({ 'error': 'Invalid favorite properties.' }), 400
    favorites.append(newFavorite)
    favoriteToSave = Favorite(data=newFavorite)
    db.session.add(favoriteToSave)
    db.session.commit()
    return '', 201, { 'location': f'/favorites/{newFavorite["id"]}' }


@app.route('/favorites/<int:id>', methods=['DELETE'])
def delete_favorite(id: int):
    global favorites
    selectedFavorite = get_favorite(id)
    if selectedFavorite is None:
        return jsonify({ 'error': 'favorite does not exist.' }), 404
    favorites = [e for e in favorites if e['id'] != id]
    db.session.delete(selectedFavorite)
    db.session.commit()
    return jsonify(selectedFavorite), 200


@app.route('/', methods=['GET'])
def show_info():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(port=5000)