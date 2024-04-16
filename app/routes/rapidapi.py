from app import app, db
from app.models import User, Post, Comment, Favorite
from app.utils import *
#from config import Config
from flask import jsonify, request, render_template
from flask_cors import cross_origin
import json
import requests
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from PRIVATE_API_KEY import PRIVATE_API_KEY

#Ok działa
@app.route('/api/search', methods=['POST'])
@cross_origin()
def fetch_receipes():
    data_str = request.data.decode('utf-8')
    data_dict = json.loads(data_str)

    ingredients_array = (data_dict.get('ingredients', False))
    excluded_array = (data_dict.get('excluded', False))
    params_array = (data_dict.get('params', False))
    link_next_page = (data_dict.get('link_next_page'), False)
    
    headers = {
        "Accept-Language": "en",
        "X-RapidAPI-Key": PRIVATE_API_KEY,
        'Content-Type': 'application/json',
        "X-RapidAPI-Host": "edamam-recipe-search.p.rapidapi.com"
    }
    
    if link_next_page[0]:
        url = link_next_page[0]['href']
        querystring = None
    else:
        url = "https://edamam-recipe-search.p.rapidapi.com/api/recipes/v2"
        querystring = {
            "type":"any",
            #"random":"true"
        }
        
        diet_labels = ['low-carb', 'low-fat']
        health_labels = ['vegan', 'vegetarian', 'gluten-free', 'alcohol-free']
        excluded_index = 0
        health_index = 0
        diet_index = 0
        
        if ingredients_array:
            querystring["q"] = ' '.join(ingredients_array)
        
        if excluded_array:
            for single_excluded in excluded_array:
                querystring[f"excluded[{excluded_index}]"] = single_excluded
                excluded_index += 1
            
        if params_array:
            for single_param in params_array:
                if single_param in diet_labels:
                    querystring[f"diet[{diet_index}]"] = single_param
                    diet_index += 1
                elif single_param in health_labels:
                    querystring[f"health[{health_index}]"] = single_param
                    health_index += 1
        
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response_data = response.json()
        
        search_results = {
            'count': response_data['count'],
            'hits': [],
            '_links': response_data['_links'],
        }
        for single_hit in response_data['hits']:
            single_result = {
                'url': single_hit['recipe']['url'],
                'image_SMALL_url': single_hit['recipe']['images']['SMALL']['url'],
                'image_REGULAR_url':  single_hit['recipe']['images']['REGULAR']['url'],
                'label': single_hit['recipe']['label'],
                'dishType': single_hit['recipe']['dishType'],
                'mealType': single_hit['recipe']['mealType'],
                'cuisineType': single_hit['recipe']['cuisineType'],
                'cautions': single_hit['recipe']['cautions'],
                'totalTime': single_hit['recipe']['totalTime'],
                'dietLabels': single_hit['recipe']['dietLabels'],
                'healthLabels': single_hit['recipe']['healthLabels'],
                'calories': single_hit['recipe']['calories'],
            }
            search_results['hits'].append(single_result)
        return search_results
    except Exception as error:
        return jsonify({ 'error': f'{error}' }), 500

#Ok działa
@app.route('/api/quote', methods=['GET'])
@cross_origin()
def fetch_quotes():
    main_url = 'https://famous-quotes4.p.rapidapi.com/random?'
    category = f"category={get_random_topic(['fitness', 'food', 'health'])}"
    count = '&count=1'
    url = f"{main_url}{category}{count}"
    headers = {
        'X-RapidAPI-Key': PRIVATE_API_KEY,
        'X-RapidAPI-Host': 'famous-quotes4.p.rapidapi.com'
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as error:
        return jsonify({ 'error': f'{error}' }), 500