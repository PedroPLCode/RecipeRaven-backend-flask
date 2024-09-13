from app import app, db
from app.models import (
    User, 
    Post, 
    Comment, 
    PostLikeIt, 
    PostHateIt, 
    Reaction, 
    ReactionLikeIt, 
    ReactionHateIt, 
    News, 
    NewsLikeIt, 
    NewsHateIt, 
    Comment, 
    CommentLikeIt, 
    CommentHateIt
    )
from app.utils import *
from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime as dt
from flask_jwt_extended import get_jwt_identity, jwt_required
from config import Config

@app.route('/api/posts', methods=['GET'])
@cross_origin()
def get_posts():
    try:
        all_posts = Post.query.all()
        results = [process_post_news(post) for post in all_posts]
        return {"msg": 'Posts downloaded succesfully.', 'results': results}, 200
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/api/posts', methods=['POST'])
@cross_origin()
@jwt_required(optional=True)
def create_post():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data["title"] or not data["content"]:
            return jsonify({"msg": "No input data provided or wrong data."}), 400
        
        user = User.query.filter_by(
            login=current_user).first_or_404() if current_user else None

        new_post = Post(title=data["title"], 
                        content=data["content"], 
                        guest_author=data["guest_author"] if not user else None, 
                        user_id=user.id if user else None)
        db.session.add(new_post)
        db.session.commit()
        
        return jsonify({"msg": "Post created successfully",
                        "location": f'/posts/{new_post.id}'}), 201
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@cross_origin()
@jwt_required()
def update_post(post_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data["title"] or not data["content"]:
            return jsonify({"msg": "No input data provided."}), 400
        
        user = User.query.filter_by(login=current_user).first_or_404()
        
        if not user:
            return jsonify({"msg": "Error. User not found."}), 400
        
        post = Post.query.filter(
            (Post.id == post_id) & 
            ((Post.user_id == user.id) | (user.role == 'admin'))
        ).first_or_404()
        
        if not post:
            return jsonify({"msg": "Error. Post not found."}), 400
        
        if data["content"] == '' and data["title"] == '':
            
            post_comments = Comment.query.filter(
                Comment.post_id == post.id
                ).first()
            if post_comments:
                return jsonify({"msg": "Post still have comments. Cant delete."}), 400
            
            db.session.delete(post)
            db.session.commit()
            return jsonify({"msg": "Post deleted."}), 400
        else:
            post.title = data["title"]
            post.content = data["content"]
            post.last_update = dt.utcnow()
            db.session.commit()
            return jsonify({"msg": "Post updated successfully.", 
                            "location": f'/posts/{post.id}'}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_post(post_id):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        
        if not user:
            return jsonify({"msg": "Error. User not found."}), 400        
        
        if user:
            post_to_delete = Post.query.filter(
            (Post.id == post_id) & 
            ((Post.user_id == user.id) | (user.role == 'admin'))
        ).first_or_404()
            
            if not post_to_delete:
                return jsonify({"msg": "Error. Post not found."}), 400
        
            post_comments = Comment.query.filter(
                Comment.post_id == post_to_delete.id
                ).first()
            if post_comments:
                return jsonify({"msg": "Post still have comments. Cant delete."}), 400
            
            else: 
                db.session.delete(post_to_delete)
                db.session.commit()
                return jsonify({"msg": "Post deleted succesfully."}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401
    

@app.route('/api/<string:object_type>/<string:action>/<int:object_id>', methods=['POST'])
@cross_origin()
@jwt_required()
def manage_reaction(action, object_type, object_id):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()
        
        model_map = {
            'comments': (Comment, CommentLikeIt, CommentHateIt, 'comment_id'),
            'posts': (Post, PostLikeIt, PostHateIt, 'post_id'),
            'news': (News, NewsLikeIt, NewsHateIt, 'news_id'),
            'reactions': (Reaction, ReactionLikeIt, ReactionHateIt, 'reaction_id')
        }

        if object_type not in model_map:
            return jsonify({"message": "Invalid object type"}), 400

        model_class, like_class, hate_class, parent_field = model_map[object_type]
        obj = model_class.query.filter_by(id=object_id).first_or_404()
        
        if user.id == obj.user_id:
            return jsonify({"msg": f'You cant add {action} to your own {object_type}.'}), 500
        
        like_filter = (like_class.query
                        .filter_by(user_id=user.id)
                        .filter(getattr(like_class, parent_field) == obj.id))
        like_exists = like_filter.first()

        hate_filter = (hate_class.query
                        .filter_by(user_id=user.id)
                        .filter(getattr(hate_class, parent_field) == obj.id))
        hate_exists = hate_filter.first()

        if action == 'like':
            opposite_reaction = hate_exists
            existing_reaction = like_exists
            reaction_class = like_class
            opposite_msg = "Hate removed. "
            reaction_msg = "Like added successfully."
            delete_msg = "Like deleted successfully."
        elif action == 'hate':
            opposite_reaction = like_exists
            existing_reaction = hate_exists
            reaction_class = hate_class
            opposite_msg = "Like removed. "
            reaction_msg = "Hate added successfully."
            delete_msg = "Hate deleted successfully."
        else:
            return jsonify({"msg": "Invalid action."}), 400

        if existing_reaction:
            db.session.delete(existing_reaction)
            db.session.commit()
            return jsonify({"msg": delete_msg}), 200

        if opposite_reaction:
            db.session.delete(opposite_reaction)
            db.session.commit()

        new_reaction = reaction_class(user_id=user.id)
        setattr(new_reaction, parent_field, obj.id)

        db.session.add(new_reaction)
        db.session.commit()
        return jsonify({"msg": opposite_msg + reaction_msg}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500