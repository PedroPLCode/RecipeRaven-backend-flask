from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
import json
import bcrypt
import random
import requests
import json
import requests
import os.path
from PRIVATE_API_KEY import PRIVATE_API_KEY
                               
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
    
    
class Board(db.Model):
    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON, nullable=False)
    
    
db_url = 'sqlite:///favorites.db'
engine = create_engine(db_url)
Favorite.metadata.create_all(engine)
Board.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
    
favorites = []
board = []

nextFavoriteId = 1
nextNewPostId = 1


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


@app.route('/search', methods=['POST'])
@cross_origin()
def fetch_receipes():
    data_str = request.data.decode('utf-8')
    data_dict = json.loads(data_str)

    ingredients_array = (data_dict.get('ingredients', False))
    excluded_array = (data_dict.get('excluded', False))
    params_array = (data_dict.get('params', False))
    link_next_page = (data_dict.get('link_next_page'), False)
    
    headers = {
        "Accept-Language": "en",
        "X-RapidAPI-Key": PRIVATE_API_KEY,
        'Content-Type': 'application/json',
        "X-RapidAPI-Host": "edamam-recipe-search.p.rapidapi.com"
    }
    
    if link_next_page[0]:
        url = link_next_page[0]['href']
        querystring = None
    else:
        url = "https://edamam-recipe-search.p.rapidapi.com/api/recipes/v2"
        querystring = {
            "type":"any",
            #"random":"true"
        }
        
        diet_labels = ['low-carb', 'low-fat']
        health_labels = ['vegan', 'vegetarian', 'gluten-free', 'alcohol-free']
        excluded_index = 0
        health_index = 0
        diet_index = 0
        
        if ingredients_array:
            querystring["q"] = ' '.join(ingredients_array)
        
        if excluded_array:
            for single_excluded in excluded_array:
                querystring[f"excluded[{excluded_index}]"] = single_excluded
                excluded_index += 1
            
        if params_array:
            for single_param in params_array:
                if single_param in diet_labels:
                    querystring[f"diet[{diet_index}]"] = single_param
                    diet_index += 1
                elif single_param in health_labels:
                    querystring[f"health[{health_index}]"] = single_param
                    health_index += 1
        
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response_data = response.json()
        
        search_results = {
            'count': response_data['count'],
            'hits': [],
            '_links': response_data['_links'],
        }
        for single_hit in response_data['hits']:
            single_result = {
                'url': single_hit['recipe']['url'],
                'image_SMALL_url': single_hit['recipe']['images']['SMALL']['url'],
                'image_REGULAR_url':  single_hit['recipe']['images']['REGULAR']['url'],
                'label': single_hit['recipe']['label'],
                'dishType': single_hit['recipe']['dishType'],
                'mealType': single_hit['recipe']['mealType'],
                'cuisineType': single_hit['recipe']['cuisineType'],
                'cautions': single_hit['recipe']['cautions'],
                'totalTime': single_hit['recipe']['totalTime'],
                'dietLabels': single_hit['recipe']['dietLabels'],
                'healthLabels': single_hit['recipe']['healthLabels'],
                'calories': single_hit['recipe']['calories'],
            }
            search_results['hits'].append(single_result)
        return search_results
    except Exception as error:
        return jsonify({ 'error': f'{error}' }), 500


def get_random_topic(array):
    min_val = 0
    max_val = len(array) - 1
    random_index = get_random_int_inclusive(min_val, max_val)
    return array[random_index]


def get_random_int_inclusive(min_val, max_val):
    return random.randint(min_val, max_val)


@app.route('/quote', methods=['GET'])
@cross_origin()
def fetch_quotes():
    main_url = 'https://famous-quotes4.p.rapidapi.com/random?'
    category = f"category={get_random_topic(['fitness', 'food', 'health'])}"
    count = '&count=1'
    url = f"{main_url}{category}{count}"
    headers = {
        'X-RapidAPI-Key': PRIVATE_API_KEY,
        'X-RapidAPI-Host': 'famous-quotes4.p.rapidapi.com'
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as error:
        return jsonify({ 'error': f'{error}' }), 500
  

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


def item_is_valid(item):
    for key in item.keys():
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
    if not item_is_valid(newFavorite):
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


@app.route('/board', methods=['GET'])
@cross_origin()
def get_board():
    try:
        dataLoadedFromDB = db.session.execute(db.select(Board))
        if not isinstance(board, list):
            board.append(dataLoadedFromDB)
    except Exception as error:
        return str(error)
    return jsonify(board)


@app.route('/board', methods=['POST'])
@cross_origin()
def create_new_post():
    global nextNewPostId
    newPost = {}
    newPost['data'] = json.loads(request.data)
    newPost['id'] = nextNewPostId
    nextNewPostId += 1
    if not item_is_valid(newPost):
        return jsonify({ 'error': 'Invalid favorite properties.' }), 400
    board.append(newPost)
    newPostToSave = Board(data=newPost)
    db.session.add(newPostToSave)
    db.session.commit()
    return '', 201, { 'location': f'/board/{newPost["id"]}' }


@app.route('/', methods=['GET'])
def show_info():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, port=5000)