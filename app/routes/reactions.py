from app import app, db
from app.models import User, Reaction, News
from app.utils import *
from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime as dt
from flask_jwt_extended import get_jwt_identity, jwt_required
from config import Config
from sqlalchemy.orm import joinedload

@app.route('/api/reactions', methods=['GET'])
@cross_origin()
def get_reactions():
    try:
        all_reactions = Reaction.query.all()
        results = []
        for reaction in all_reactions:
            temp = {}
            temp['content'] = reaction.content
            temp['author'] = reaction.user.name if reaction.user else None
            temp['guest_author'] = reaction.guest_author if reaction.guest_author else None
            temp['author_picture'] = reaction.user.picture if reaction.user else None
            results.append(temp)
        return results
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/api/reactions', methods=['POST'])
@cross_origin()
@jwt_required(optional=True)
def create_reaction():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() if current_user else None
        
        new_reaction = Reaction(news_id=data["news_id"], content=data["content"], guest_author=data["guest_author"] if not user else None, user_id=user.id if user else None)
        
        db.session.add(new_reaction)
        db.session.commit()
        return jsonify({"message": "Reaction created successfully", "location": f'/reactions/{new_reaction.id}'}), 201
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/api/reactions/<int:reaction_id>', methods=['PUT'])
@cross_origin()
@jwt_required()
def update_reaction(reaction_id):
    try:
        data = request.get_json()
        
        if not data or not data["content"]:
            return jsonify({"message": "No input data provided or missing data"}), 400
        
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()
        reaction = Reaction.query.filter(
            (Reaction.id == reaction_id) & 
            ((Reaction.user_id == user.id) | (user.id == Config.admin_id))
        ).first_or_404()
        
        reaction.content = data["content"]
        reaction.last_update = dt.utcnow()
        
        db.session.commit()
        
        return jsonify({"message": "Reaction updated successfully", "location": f'/reactions/{reaction.id}'}), 200
    except Exception as e:
        return {"msg": str(e)}, 401
    

@app.route('/api/reactions/<int:reaction_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_reaction(reaction_id):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()

        reaction_to_delete = Reaction.query.filter(
            (Reaction.id == reaction_id)
        ).join(News).filter(
            (Reaction.user_id == user.id) | 
            (user.id == Config.admin_id) | 
            (News.user_id == user.id)
        ).first_or_404()

        db.session.delete(reaction_to_delete)
        db.session.commit()

        return jsonify({"msg": "Reaction deleted successfully"}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401