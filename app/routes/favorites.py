from app import app, db
from app.models import User, Favorite, Note
from app.utils import *
from flask import jsonify, request
from flask_cors import cross_origin
import json
import requests
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename
import os

@app.route('/api/favorites', methods=['GET'])
@cross_origin()
@jwt_required()
def get_favorites():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()
        favorites = Favorite.query.filter_by(user_id=user.id).all()
        results = []
        
        for favorite in favorites:
            favorite_data = favorite.data.copy() 
            favorite_data['id'] = favorite.id
            note = Note.query.filter_by(favorite_id=favorite.id).first()
            favorite_data['note'] = note.to_dict() if note else None
            favorite_data['starred'] = True if favorite.starred else False
            results.append(favorite_data)
        
        return jsonify(results), 200
    except Exception as e:
        return {"msg": str(e)}, 401
    

@app.route('/api/favorites', methods=['POST'])
@cross_origin()
@jwt_required()
def create_favorite():
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404(
            description="User not found."
        )

        if user:
            new_favorite = {}
            new_favorite['data'] = json.loads(request.data)
            
            try:
                calories_value = int(new_favorite['data']['calories'])
                user_favorites = Favorite.query.filter_by(user_id=user.id).all()
                for single_favorite in user_favorites:
                    single_favorite_calories = int(
                        single_favorite.data.get('data', {}).get('calories', 0)
                        )
                    if single_favorite_calories == calories_value:
                        return jsonify({"msg": "Favorite already exists."}), 400
            except Exception as e:
                return jsonify({"msg": f"Error querying database: {e}"}), 500
            
            image_url = (
                new_favorite['data'].get('image_REGULAR_url') or 
                new_favorite['data'].get('image_SMALL_url')
            )
            if image_url:
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    return {"msg": f"Failed to fetch image from URL: {str(e)}"}, 400

                filename = secure_filename(os.path.basename(image_url))
                if len(filename) > 255:
                    filename = filename[:255]

                image_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
                try:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    new_favorite['image_name'] = filename
                except Exception as e:
                    return {"msg": f"Failed to save image: {str(e)}"}, 500

            favorite = Favorite(data=new_favorite, user_id=user.id, starred=False)
            db.session.add(favorite)
            note = Note(favorite_id=favorite.id, content='')
            db.session.add(note)
            db.session.commit()
            
            return '', 201, {'location': f'/favorites/{favorite.id}'}
        
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/api/favorites/<int:favorite_to_delete_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_favorite(favorite_to_delete_id: int):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404(
            description="User not found."
        )
        favorite_to_delete = Favorite.query.filter_by(
            id=favorite_to_delete_id, user_id=user.id).first_or_404(
                description="Favorite not found."
            )
        note_to_delete = Note.query.filter_by(favorite_id=favorite_to_delete.id).first()

        try:
            if 'image_name' in favorite_to_delete.data:
                image_name = favorite_to_delete.data['image_name']
                image_to_delete = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], 
                                               image_name)
                if os.path.exists(image_to_delete):
                    os.remove(image_to_delete)
                else:
                    pass

            if note_to_delete:
                db.session.delete(note_to_delete)
            db.session.delete(favorite_to_delete)
            db.session.commit()
            
            return jsonify({"msg": "Favorite and associated note deleted successfully", 
                            "favorite": favorite_to_delete.to_dict()}), 200
            
        except Exception as e:
            db.session.rollback()
            return {"msg": f"An error occurred during deletion: {str(e)}"}, 500
    except Exception as e:
        return {"msg": str(e)}, 404
    

@app.route('/api/favorites/starred/<int:favorite_id>', methods=['POST'])
@cross_origin()
@jwt_required()
def handle_starred_favorite(favorite_id: int):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404(
            description="User not found"
            )
        favorite = Favorite.query.filter_by(
            id=favorite_id, user_id=user.id).first_or_404(
                description="Favorite not found"
            )
            
        favorite.starred = not favorite.starred
        db.session.commit()
        
        return jsonify({"msg": "Operation successful", 
                        "favorite": favorite.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500