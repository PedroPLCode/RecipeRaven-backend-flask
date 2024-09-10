from app import app
from app.utils import *
from flask import jsonify, request
from flask_cors import cross_origin
import os
import json
import requests

PRIVATE_API_KEY = os.environ['PRIVATE_API_KEY']

@app.route('/api/search', methods=['POST'])
@cross_origin()
def fetch_receipes():
    data_str = request.data.decode('utf-8')
    data_dict = json.loads(data_str)

    ingredients_array = (data_dict.get('ingredients', False))
    excluded_array = (data_dict.get('excluded', False))
    params_array = (data_dict.get('params', False))
    random = (data_dict.get('random', False))
    link_next_page = (data_dict.get('link_next_page'), False)
    
    diet_labels = ['low-carb', 'low-fat']
    health_labels = ['vegan', 'vegetarian', 'gluten-free', 'alcohol-free']
    
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
            "type": "any",
            "random": random,
        }
        
        if ingredients_array:
            querystring["q"] = ingredients_array
        
        if excluded_array:
            querystring["excluded"] = excluded_array

        if isinstance(params_array, list):
            querystring["diet"] = [single_param for single_param in params_array if single_param in diet_labels]
            querystring["health"] = [single_param for single_param in params_array if single_param in health_labels]
                    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response_data = response.json()
        
        search_results = {
            'count': response_data['count'],
            'hits': [],
            '_links': response_data['_links'],
        }
        
        for single_hit in response_data['hits']:
            single_result = {}
            
            if 'dishType' in single_hit['recipe']:
                single_result['dishType'] = single_hit['recipe']['dishType']
            if 'url' in single_hit['recipe']:
                single_result['url'] = single_hit['recipe']['url']   
            if 'label' in single_hit['recipe']:
                single_result['label'] = single_hit['recipe']['label']
            if 'mealType' in single_hit['recipe']:
                single_result['mealType'] = single_hit['recipe']['mealType'] 
            if 'cuisineType' in single_hit['recipe']:
                single_result['cuisineType'] = single_hit['recipe']['cuisineType']
            if 'cautions' in single_hit['recipe']:
                single_result['cautions'] = single_hit['recipe']['cautions']
            if 'totalTime' in single_hit['recipe']:
                single_result['totalTime'] = single_hit['recipe']['totalTime']
            if 'dietLabels' in single_hit['recipe']:
                single_result['dietLabels'] = single_hit['recipe']['dietLabels']
            if 'healthLabels' in single_hit['recipe']:
                single_result['healthLabels'] = single_hit['recipe']['healthLabels']                
            if 'calories' in single_hit['recipe']:
                single_result['calories'] = single_hit['recipe']['calories']                
            if 'images' in single_hit['recipe']:
                images = single_hit['recipe']['images']
                if 'SMALL' in images:
                    small = images['SMALL']
                    if 'url' in small:
                        single_result['image_SMALL_url'] = small['url']
                if 'REGULAR' in images:
                    regular = images['REGULAR']
                    if 'url' in regular:
                        single_result['image_REGULAR_url'] = regular['url']
            
            search_results['hits'].append(single_result)
        return search_results
    except Exception as error:
        return jsonify({ 'msg': f'{error}' }), 500


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
        return jsonify({ 'msg': f'{error}' }), 500