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

@app.route('/posts', methods=['GET'])
@cross_origin()
def get_posts():
    try:
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
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/posts', methods=['POST'])
@cross_origin()
@jwt_required()
def create_post():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        new_post = Post(title=data["title"], content=data["content"], user_id=user.id)
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"message": "Post created successfully", "location": f'/posts/{new_post.id}'}), 201
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_post(post_id: int):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        
        if user:
            item_to_delete = Post.query.filter_by(id=post_id, user_id=user.id).first_or_404()  
            db.session.delete(item_to_delete)
            db.session.commit()
            return jsonify(item_to_delete), 200
    except Exception as e:
        return {"msg": str(e)}, 401