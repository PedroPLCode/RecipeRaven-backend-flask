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

#logging dodać
#pytests dodać

app.secret_key = b'my-super-top-secret-key'

#Ok działa
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

#Ok działa
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
  

#ok działa
@app.route('/favorites', methods=['GET'])
@cross_origin()
def get_favorites():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        results = []
        favorites = Favorite.query.filter_by(user_id=user.id).all()
        for favorite in favorites:
            favorite.data['id'] = favorite.id
            results.append(favorite.data)
        return results
    except Exception as e:
        return {"msg": str(e)}, 401
    

#ok działa
@app.route('/favorites', methods=['POST'])
@cross_origin()
@jwt_required()
def create_favorite():
    current_user = get_jwt_identity()
    user = User.query.filter_by(login=current_user).first_or_404() 
    new_favorite = {}
    new_favorite['data'] = json.loads(request.data)
    favorite = Favorite(data=new_favorite, user_id=user.id if current_user else None)
    db.session.add(favorite)
    db.session.commit()
    return '', 201, { 'location': f'/favorites/{new_favorite.id}' }


#ok działa
@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_favorite(favorite_id: int):
    item_to_delete = Favorite.query.filter_by(id=favorite_id).first_or_404()  
    db.session.delete(item_to_delete)
    db.session.commit()
    return jsonify(item_to_delete), 200


@app.route('/posts', methods=['GET'])
@cross_origin()
def get_posts():
    all_users = User.query.all() 
    all_posts = Post.query.all()
    results = []
    for post in all_posts:
        temp = {}
        temp['content'] = post.content
        temp['title'] = post.title
        temp['author'] = post.user.name
        results.append(temp)
    return results


@app.route('/posts', methods=['POST'])
@cross_origin()
@jwt_required()
def create_post():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    
    current_user = get_jwt_identity()
    user = User.query.filter_by(login=current_user).first_or_404() 
    new_post = Post(title=data["title"], content=data["content"], user_id=user.id)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"message": "Post created successfully", "location": f'/posts/{new_post.id}'}), 201


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_post(post_id: int):
    item_to_delete = Post.query.filter_by(id=post_id).first_or_404()  
    db.session.delete(item_to_delete)
    db.session.commit()
    return jsonify(item_to_delete), 200


@app.route('/comments', methods=['GET'])
@cross_origin()
def get_comments():
    all_comments = Comment.query.all()
    return jsonify(all_comments)


@app.route('/comments', methods=['POST'])
@cross_origin()
def create_comment():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    
    current_user = get_jwt_identity()
    user = User.query.filter_by(login=current_user).first_or_404() 
    new_comment = Comment(content=data["content"], user_id=user.id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({"message": "Comment created successfully", "location": f'/comments/{new_comment.id}'}), 201


@app.route('/comments/<int:comment_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_comment(comment_id: int):
    item_to_delete = Comment.query.filter_by(id=comment_id).first_or_404()  
    db.session.delete(item_to_delete)
    db.session.commit()
    return jsonify(item_to_delete), 200


@app.route('/', methods=['GET'])
def show_info():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, port=5000)