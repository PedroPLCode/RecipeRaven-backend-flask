from app import app, db
from app.models import User, Post, Comment, Favorite, Note
from app.utils import *
#from config import Config
from flask import jsonify, request, render_template
from flask_cors import cross_origin
import json
import requests
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from PRIVATE_API_KEY import PRIVATE_API_KEY
    

@app.route('/api/notes', methods=['POST'])
@cross_origin()
@jwt_required()
def create_note():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"message": "No input data provided"}), 400

        note = Note.query.filter_by(favorite_id=data["favorite_id"]).first()
        if note:
            note.content = data["content"]
        else:
            new_note = Note(favorite_id=data["favorite_id"], content=data["content"])
            db.session.add(new_note)

        db.session.commit()
        return '', 201, {'location': f'/notes/{note.id if note else new_note.id}'}
    except Exception as e:
        return jsonify({"msg": str(e)}), 401