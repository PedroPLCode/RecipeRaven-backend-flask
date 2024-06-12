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

@app.route('/api/comments', methods=['GET'])
@cross_origin()
def get_comments():
    try:
        all_users = User.query.all() 
        all_comments = Comment.query.all()
        results = []
        for comment in all_comments:
            temp = {}
            temp['content'] = comment.content
            temp['author'] = comment.user.name if comment.user else None
            temp['guest_author'] = comment.guest_author if comment.guest_author else None
            temp['author_picture'] = comment.user.picture if comment.user else None
            results.append(temp)
        return results
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/api/comments', methods=['POST'])
@cross_origin()
@jwt_required(optional=True)
def create_comment():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() if current_user else None
        
        new_comment = Comment(post_id=data["post_id"], content=data["content"], guest_author=data["guest_author"] if not user else None, user_id=user.id if user else None)
        
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({"message": "Comment created successfully", "location": f'/comments/{new_comment.id}'}), 201
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
#PUT 


@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_comment(comment_id: int):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        item_to_delete = Comment.query.filter_by(id=comment_id, user_id=user.id).first_or_404()  
        db.session.delete(item_to_delete)
        db.session.commit()
        return jsonify(item_to_delete), 200
    except Exception as e:
        return {"msg": str(e)}, 401