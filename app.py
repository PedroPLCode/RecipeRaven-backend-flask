import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

favorites = [
    { 'id': 1, 'name': 'carrot' },
    { 'id': 2, 'name': 'corn' },
    { 'id': 3, 'name': 'tomato' }
]

nextFavoriteId = 4
#3

@app.route('/favorites', methods=['GET'])
@cross_origin()
def get_favorites():
    return jsonify(favorites)

@app.route('/favorites/<int:id>', methods=['GET'])
def get_favorite_by_id(id: int):
    favorite = get_favorite(id)
    if favorite is None:
        return jsonify({ 'error': 'favorite does not exist'}), 404
    return jsonify(favorite)

def get_favorite(id):
    return next((f for f in favorites if f['id'] == id), None)

def favorite_is_valid(favorite):
    for key in favorite.keys():
        if key != 'name':
            return False
    return True

@app.route('/favorites', methods=['POST'])
def create_favorite():
    global nextfavoriteId
    favorite = json.loads(request.data)
    #if not favorite_is_valid(favorite):
    #    return jsonify({ 'error': 'Invalid favorite properties.' }), 400
    favorite['id'] = nextfavoriteId
    nextfavoriteId += 1
    favorites.append(favorite)
    return '', 201, { 'location': f'/favorites/{favorite["id"]}' }

@app.route('/favorites/<int:id>', methods=['PUT'])
def update_favorite(id: int):
    favorite = get_favorite(id)
    if favorite is None:
        return jsonify({ 'error': 'favorite does not exist.' }), 404
    updated_favorite = json.loads(request.data)
    if not favorite_is_valid(updated_favorite):
        return jsonify({ 'error': 'Invalid favorite properties.' }), 400
    favorite.update(updated_favorite)
    return jsonify(favorite)

@app.route('/favorites/<int:id>', methods=['DELETE'])
def delete_favorite(id: int):
    global favorites
    favorite = get_favorite(id)
    if favorite is None:
        return jsonify({ 'error': 'favorite does not exist.' }), 404
    favorites = [e for e in favorites if e['id'] != id]
    return jsonify(favorite), 200

@app.route('/', methods=['GET'])
def show_info():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(port=5000)

