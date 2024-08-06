from app import app, db
from app.models import User, News, Reaction
from app.utils import *
from flask import jsonify, request
from flask_cors import cross_origin
from datetime import datetime as dt
from flask_jwt_extended import get_jwt_identity, jwt_required, JWTManager
from config import Config

@app.route('/api/news', methods=['GET'])
@cross_origin()
def get_news():
    try:
        all_news = News.query.all()
        results = []
        
        for news in all_news:
            creation_date_str = str(news.creation_date) if news.creation_date else None
            creation_date_obj = dt.strptime(creation_date_str, "%Y-%m-%d %H:%M:%S.%f") if creation_date_str else None
            formatted_creation_date = creation_date_obj.strftime("%Y-%m-%d %H:%M:%S CET") if creation_date_obj else None
            modification_date_str = str(news.last_update) if news.last_update else None
            modification_date_obj = dt.strptime(modification_date_str, "%Y-%m-%d %H:%M:%S.%f") if modification_date_str else None
            formatted_modification_date = modification_date_obj.strftime("%Y-%m-%d %H:%M:%S CET") if modification_date_obj else None
            temp = {
                'id': news.id,
                'user_id': news.user_id,
                'content': news.content,
                'title': news.title,
                'creation_date': formatted_creation_date,
                'last_update': formatted_modification_date,
                'reactions': []
            }

            #news_reactions = Reaction.query.filter_by(news_id=news.id).all()
            for reaction in news.reactions:
                creation_date_str = str(reaction.creation_date) if reaction.creation_date else None
                creation_date_obj = dt.strptime(creation_date_str, "%Y-%m-%d %H:%M:%S.%f") if creation_date_str else None
                formatted_creation_date = creation_date_obj.strftime("%Y-%m-%d %H:%M:%S CET") if creation_date_obj else None
                modification_date_str = str(reaction.last_update) if reaction.last_update else None
                modification_date_obj = dt.strptime(modification_date_str, "%Y-%m-%d %H:%M:%S.%f") if modification_date_str else None
                formatted_modification_date = modification_date_obj.strftime("%Y-%m-%d %H:%M:%S CET") if modification_date_obj else None
                temp['reactions'].append({
                    'id': reaction.id,
                    'user_id': reaction.user_id,
                    'content': reaction.content,
                    'author': reaction.user.name or reaction.user.login if reaction.user else None,
                    'guest_author': reaction.guest_author if reaction.guest_author else None,
                    'creation_date': formatted_creation_date,
                    'last_update': formatted_modification_date,
                })
                
            results.append(temp)
        
        return results
    except Exception as e:
        return {"msg": str(e)}, 401


@app.route('/api/news', methods=['POST'])
@cross_origin()
@jwt_required()
def create_news():
    try:
        data = request.get_json()
        
        if not data or not data["title"] or not data["content"]:
            return jsonify({"message": "No input data provided or missing data"}), 400
        
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() if current_user else None

        new_news = News(title=data["title"], content=data["content"], user_id=user.id if user else None)
        
        db.session.add(new_news)
        db.session.commit()
        return jsonify({"message": "News created successfully", "location": f'/posts/{new_news.id}'}), 201
    except Exception as e:
        return {"msg": str(e)}, 401
    
    
@app.route('/api/news/<int:news_id>', methods=['PUT'])
@cross_origin()
@jwt_required()
def update_news(news_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404()
        news = News.query.filter(
            (News.id == news_id) & 
            ((News.user_id == user.id) | (user.id == Config.admin_id))
        ).first_or_404()
        
        if data["content"] == '' and data["title"] == '':
            db.session.delete(news)
        else:
            news.title = data["title"]
            news.content = data["content"]
            news.last_update = dt.utcnow()
        
        db.session.commit()
        
        return jsonify({"message": "News updated successfully", "location": f'/posts/{news.id}'}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401


@app.route('/api/news/<int:news_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_news(news_id):
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(login=current_user).first_or_404() 
        
        if user:
            news_to_delete = News.query.filter(
            (News.id == news_id) & 
            ((News.user_id == user.id) | (user.id == Config.admin_id))
        ).first_or_404()
            
            news_reactions = Reaction.query.filter(Reaction.news_id == news_to_delete.id).first()
            if news_reactions:
                return {'Error. News still have reactions. Cant delete'}, 400
            else: 
                db.session.delete(news_to_delete)
                db.session.commit()
                return jsonify(news_to_delete), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 401