from app import app, db
from app.models import Note
from app.utils import *
from flask import jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required

@app.route('/api/notes', methods=['POST'])
@cross_origin()
@jwt_required()
def create_note():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"msg": "No input data provided."}), 400

        note = Note.query.filter_by(favorite_id=data["favorite_id"]).first()
        if note:
            if data["content"] == '':
                db.session.delete(note)
                db.session.commit()
                return jsonify({"msg": "Note deleted."}), 400
            else:
                note.content = data["content"]
                db.session.commit()
                return jsonify({"msg": "Note updated."}), 400
        else:
            new_note = Note(favorite_id=data["favorite_id"], 
                            content=data["content"])
            db.session.add(new_note)
            db.session.commit()
            return jsonify({"msg": "Note created."}), 400
        
    except Exception as e:
        return jsonify({"msg": str(e)}), 401