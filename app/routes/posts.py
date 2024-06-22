from app import app, db
from app.models import User, Post, Comment
from app.utils import *
from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime as dt
from flask_jwt_extended import get_jwt_identity, jwt_required, JWTManager
from config import Config

@app.route('/api/posts', methods=['GET'])
@cross_origin()
def get_posts():
    try:
        all_posts = Post.query.all()
        results = []
        
        for post in all_posts:
            temp = {
                'id': post.id,
                'user_id': post.user_id,
                'content': post.content,
                'title': post.title,
                'author': post.user.name or post.user.login if post.user else None,
                'guest_author': post.guest_author if post.guest_author else None,
                'author_picture': post.user.picture if post.user else None,
                'creation_date': post.creation_date,
                'last_update': post.last_update,
                'comments': []
            }

            post_comments = Comment.query.filter_by(post_id=post.id).all()
            for comment in post_comments:
                temp['comments'].append({
                    'id': comment.id,
                    'user_id': comment.user_id,
                    'content': comment.content,
                    'author': comment.user.name or comment.user.login if comment.user else None,
                    'guest_author': comment.guest_author if comment.guest_author else None,
                    'creation_date': comment.creation_date,
                    'last_update': comment.last_update,
                })
                
            results.append(temp)
        
        return results
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/api/posts', methods=['POST'])
@cross_origin()
@jwt_required(optional=True)
def create_post():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() if current_user else None

        new_post = Post(title=data["title"], content=data["content"], guest_author=data["guest_author"] if not user else None, user_id=user.id if user else None)
        
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"message": "Post created successfully", "location": f'/posts/{new_post.id}'}), 201
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@cross_origin()
@jwt_required()
def update_post(post_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()
        post = Post.query.filter(
            (Post.id == post_id) & 
            ((Post.user_id == user.id) | (user.id == Config.admin_id))
        ).first_or_404()
        
        if data["content"] == '' and data["title"] == '':
            db.session.delete(post)
        else:
            post.title = data["title"]
            post.content = data["content"]
            post.last_update = dt.utcnow()
        
        db.session.commit()
        
        return jsonify({"message": "Post updated successfully", "location": f'/posts/{post.id}'}), 200
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_post(post_id: int):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        
        if user:
            post_to_delete = Post.query.filter(
            (Post.id == post_id) & 
            ((Post.user_id == user.id) | (user.id == Config.admin_id))
        ).first_or_404()
            
            post_comments = Comment.query.filter(Comment.post_id == post_to_delete.id).first()
            if post_comments:
                return {'Error. Post still have comments. Cant delete'}, 400
            else: 
                db.session.delete(post_to_delete)
                db.session.commit()
                return jsonify(post_to_delete), 200
    except Exception as e:
        return {"msg": str(e)}, 401