from app import app, db
from app.models import User, Comment, Post
from app.utils import *
from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime as dt
from flask_jwt_extended import get_jwt_identity, jwt_required
from config import Config
from app.emails_templates import POST_COMMENT_EMAIL_BODY

@app.route('/api/comments', methods=['GET'])
@cross_origin()
def get_comments():
    try:
        all_comments = Comment.query.all()
        results = []
        for comment in all_comments:
            temp = {}
            temp['content'] = comment.content
            temp['author'] = comment.user.name or None
            temp['guest_author'] = comment.guest_author or None
            temp['author_picture'] = comment.user.picture or None
            results.append(temp)
        return results
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/api/comments', methods=['POST'])
@cross_origin()
@jwt_required(optional=True)
def create_comment():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data["content"]:
            return jsonify({"msg": "No input data provided or wrong data."}), 400
        
        user = User.query.filter_by(login=current_user).first_or_404() if current_user else None
        post = Post.query.filter_by(id=data["post_id"]).first_or_404() if data["post_id"] else None
        
        if not user:
            return jsonify({"msg": "User error. Not found."}), 400
        
        new_comment = Comment(post_id=data["post_id"], 
                              content=data["content"], 
                              guest_author=data["guest_author"] if not user else None, 
                              user_id=user.id if user else None)
        db.session.add(new_comment)
        db.session.commit()
        
        if post.user_id and not post.guest_author:
            email_subject = 'New Comment to Your Post'
            email_body = POST_COMMENT_EMAIL_BODY.format(
                username=post.user.name.title() if post.user.name else post.user.login,
                post_title=post.title,
                post_comment=new_comment.content,
                comment_author=(user.name.title() if user.name else user.login) if user else data["guest_author"]
            )
            send_email(post.user.email, email_subject, email_body)
        
        return jsonify({"msg": "Comment created successfully.", 
                        "location": f'/comments/{new_comment.id}'}), 201
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
@cross_origin()
@jwt_required()
def update_comments(comment_id):
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data["content"]:
            return jsonify({"msg": "No input data provided or wrong data."}), 400
        
        user = User.query.filter_by(login=current_user).first_or_404()
        
        if not user:
            return jsonify({"msg": "User error. Not found."}), 400
        
        comment = Comment.query.filter(
            (Comment.id == comment_id) & 
            ((Comment.user_id == user.id) | (user.role == 'admin'))
        ).first_or_404()
        
        if not comment:
                return jsonify({"msg": "Comment error. Not found."}), 400
        
        comment.content = data["content"]
        comment.last_update = dt.utcnow()
        db.session.commit()
        
        return jsonify({"msg": "Comment updated successfully.", 
                        "location": f'/comments/{comment.id}'}), 200
    except Exception as e:
        return {"msg": str(e)}, 401
    

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_comment(comment_id):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()
        
        if not user:
            return jsonify({"msg": "User error."}), 400
        
        comment_to_delete = Comment.query.filter(
            (Comment.id == comment_id)
        ).join(Post).filter(
            (Comment.user_id == user.id) | 
            (user.role == 'admin') | 
            (Post.user_id == user.id)
        ).first_or_404()
        
        if not comment_to_delete:
            return jsonify({"msg": "Comment not found."}), 400
        
        db.session.delete(comment_to_delete)
        db.session.commit()

        return jsonify({"msg": "Comment deleted successfully."}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401