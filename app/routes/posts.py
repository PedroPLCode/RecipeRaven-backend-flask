from app import app, db
from app.models import User, Post, Comment, PostLikeIt, PostHateIt, Reaction, ReactionLikeIt, ReactionHateIt, News, NewsLikeIt, NewsHateIt, Comment, CommentLikeIt, CommentHateIt
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
        results = []
        
        for post in all_posts:
            creation_date_str = str(post.creation_date) if post.creation_date else None
            creation_date_obj = dt.strptime(creation_date_str, "%Y-%m-%d %H:%M:%S.%f") if creation_date_str else None
            formatted_creation_date = creation_date_obj.strftime("%Y-%m-%d %H:%M:%S CET") if creation_date_obj else None
            modification_date_str = str(post.last_update) if post.last_update else None
            modification_date_obj = dt.strptime(modification_date_str, "%Y-%m-%d %H:%M:%S.%f") if modification_date_str else None
            formatted_modification_date = modification_date_obj.strftime("%Y-%m-%d %H:%M:%S CET") if modification_date_obj else None
            temp = {
                'id': post.id,
                'user_id': post.user_id,
                'content': post.content,
                'title': post.title,
                'author': post.user.name or post.user.login if post.user else None,
                'guest_author': post.guest_author if post.guest_author else None,
                'author_picture': post.user.picture if post.user else None,
                'author_google_user': post.user.google_user if post.user else None,
                'author_original_google_picture': post.user.original_google_picture if post.user else None,
                'creation_date': formatted_creation_date,
                'last_update': formatted_modification_date,
                'comments': [],
                'likes': [like.user_id for like in post.likes],
                'hates': [hate.user_id for hate in post.hates],
            }

            for comment in post.comments:
                creation_date_str = str(comment.creation_date) if comment.creation_date else None
                creation_date_obj = dt.strptime(creation_date_str, "%Y-%m-%d %H:%M:%S.%f") if creation_date_str else None
                formatted_creation_date = creation_date_obj.strftime("%Y-%m-%d %H:%M:%S CET") if creation_date_obj else None
                modification_date_str = str(comment.last_update) if comment.last_update else None
                modification_date_obj = dt.strptime(modification_date_str, "%Y-%m-%d %H:%M:%S.%f") if modification_date_str else None
                formatted_modification_date = modification_date_obj.strftime("%Y-%m-%d %H:%M:%S CET") if modification_date_obj else None
                temp['comments'].append({
                    'id': comment.id,
                    'user_id': comment.user_id,
                    'content': comment.content,
                    'author': comment.user.name or comment.user.login if comment.user else None,
                    'guest_author': comment.guest_author if comment.guest_author else None,
                    'creation_date': formatted_creation_date,
                    'last_update': formatted_modification_date,
                    'likes': [like.user_id for like in comment.likes],
                    'hates': [hate.user_id for hate in comment.hates],
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
        
        if not data or not data["title"] or not data["content"]:
            return jsonify({"message": "No input data provided or missing data"}), 400
        
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
        return jsonify({"msg": str(e)}), 401


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_post(post_id):
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

        like_exists = like_class.query.filter_by(user_id=user.id).filter(getattr(like_class, parent_field) == obj.id).first()
        hate_exists = hate_class.query.filter_by(user_id=user.id).filter(getattr(hate_class, parent_field) == obj.id).first()

        if action == 'like':
            opposite_reaction = hate_exists
            existing_reaction = like_exists
            reaction_class = like_class
            opposite_msg = "Hate removed. "
            reaction_msg = "Like added successfully"
            delete_msg = "Like deleted successfully"
        elif action == 'hate':
            opposite_reaction = like_exists
            existing_reaction = hate_exists
            reaction_class = hate_class
            opposite_msg = "Like removed. "
            reaction_msg = "Hate added successfully"
            delete_msg = "Hate deleted successfully"
        else:
            return jsonify({"message": "Invalid action"}), 400

        if existing_reaction:
            db.session.delete(existing_reaction)
            db.session.commit()
            return jsonify({"message": delete_msg}), 200

        if opposite_reaction:
            db.session.delete(opposite_reaction)
            db.session.commit()

        new_reaction = reaction_class(user_id=user.id)
        setattr(new_reaction, parent_field, obj.id)

        db.session.add(new_reaction)
        db.session.commit()
        return jsonify({"message": opposite_msg + reaction_msg}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500