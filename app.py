import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
from flask_login import LoginManager
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager

login_manager = LoginManager()
api = Flask(__name__)
login_manager.init_app(api)
CORS(api)
cors = CORS(api, resources={r"/favorites": {"origins": "*"}})
api.config['CORS_HEADERS'] = 'Content-Type'

api.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
api.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(api)

favorites = []

nextFavoriteId = 1

@api.after_request
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
    
@api.route('/token', methods=["POST"])
@cross_origin()
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email != "pedro" or password != "pedro":
        return {"msg": "Wrong email or password"}, 401

    access_token = create_access_token(identity=email)
    response = {"access_token":access_token}
    return response

@api.route("/logout", methods=["POST"])
@cross_origin()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@api.route('/profile')
@cross_origin()
@jwt_required()
def my_profile():
    response_body = {
        "name": "Pedro",
        "about" :"Details about Pedro"
    }

    return response_body

@api.route('/favorites', methods=['GET'])
@cross_origin()
def get_favorites():
    return jsonify(favorites)

def get_favorite(id):
    return next((f for f in favorites if f['id'] == id), None)

def favorite_is_valid(favorite):
    for key in favorite.keys():
        print(key)
        if key != 'id' and key != 'data':
            return False
    return True

@api.route('/favorites', methods=['POST'])
@cross_origin()
def create_favorite():
    global nextFavoriteId
    newFavorite = {}
    newFavorite['id'] = nextFavoriteId
    nextFavoriteId += 1
    newFavorite['data'] = json.loads(request.data)
    if not favorite_is_valid(newFavorite):
        return jsonify({ 'error': 'Invalid favorite properties.' }), 400
    favorites.append(newFavorite)
    return '', 201, { 'location': f'/favorites/{newFavorite["id"]}' }

@api.route('/favorites/<int:id>', methods=['DELETE'])
def delete_favorite(id: int):
    global favorites
    favorite = get_favorite(id)
    if favorite is None:
        return jsonify({ 'error': 'favorite does not exist.' }), 404
    favorites = [e for e in favorites if e['id'] != id]
    return jsonify(favorite), 200

@api.route('/', methods=['GET'])
def show_info():
    return render_template("index.html")

if __name__ == '__main__':
    api.run(port=5000)