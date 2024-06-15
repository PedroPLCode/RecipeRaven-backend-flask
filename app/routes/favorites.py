from app import app, db
from app.models import User, Favorite, Note
from app.utils import *
from flask import jsonify, request
from flask_cors import cross_origin
import json
import requests
from flask_jwt_extended import get_jwt_identity, jwt_required

@app.route('/api/favorites', methods=['GET'])
@cross_origin()
@jwt_required()
def get_favorites():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        
        if user:
            results = []
            favorites = Favorite.query.filter_by(user_id=user.id).all()
            for favorite in favorites:
                favorite.data['id'] = favorite.id
                
                note = Note.query.filter_by(favorite_id=favorite.id).first()
                favorite.data['note'] = note.to_dict() if note else None
                
                results.append(favorite.data)
            return results
    except Exception as e:
            return {"msg": str(e)}, 401
    

@app.route('/api/favorites', methods=['POST'])
@cross_origin()
@jwt_required()
def create_favorite():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        
        if user:
            new_favorite = {}
            new_favorite['data'] = json.loads(request.data)
            favorite = Favorite(data=new_favorite, user_id=user.id if current_user else None)
            db.session.add(favorite)
            db.session.commit()
            return '', 201, { 'location': f'/favorites/{new_favorite.id}' }
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_favorite(favorite_id: int):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        
        if user:
            favotite_to_delete = Favorite.query.filter_by(id=favorite_id, user_id=user.id).first_or_404()  
            note_to_delete = Note.query.filter_by(favorite_id=favotite_to_delete.id).first_or_404()
            db.session.delete(favotite_to_delete)
            db.session.delete(note_to_delete)
            db.session.commit()
            return jsonify(favotite_to_delete), 200
        else:
            return {"Error. Not found"}, 401
    except Exception as e:
        return {"msg": str(e)}, 401