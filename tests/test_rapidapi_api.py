import pytest
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('requests.get')
def test_fetch_recipes_success(mock_get, client):
    mock_response_data = {
        'count': 2,
        'hits': [
            {
                'recipe': {
                    'label': 'Test Recipe 1',
                    'url': 'http://example.com/recipe1',
                    'dishType': ['Main course'],
                    'mealType': ['Dinner'],
                    'cuisineType': ['Italian'],
                    'calories': 200,
                    'dietLabels': ['Low-Carb'],
                    'healthLabels': ['Vegan'],
                    'images': {
                        'REGULAR': {'url': 'http://example.com/image1.jpg'}
                    }
                }
            },
            {
                'recipe': {
                    'label': 'Test Recipe 2',
                    'url': 'http://example.com/recipe2',
                    'dishType': ['Dessert'],
                    'mealType': ['Snack'],
                    'cuisineType': ['French'],
                    'calories': 300,
                    'dietLabels': ['Low-Fat'],
                    'healthLabels': ['Gluten-Free'],
                    'images': {
                        'REGULAR': {'url': 'http://example.com/image2.jpg'}
                    }
                }
            }
        ],
        '_links': {}
    }

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response_data

    response = client.post('/api/search', json={
        'ingredients': ['tomato', 'basil'],
        'excluded': ['meat'],
        'params': ['vegan', 'low-carb'],
        'random': True
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 2
    assert len(data['hits']) == 2
    assert data['hits'][0]['label'] == 'Test Recipe 1'
    assert data['hits'][1]['label'] == 'Test Recipe 2'

@patch('requests.get')
def test_fetch_recipes_failure(mock_get, client):
    mock_get.side_effect = Exception("API call failed")

    response = client.post('/api/search', json={})
    assert response.status_code == 500
    data = response.get_json()
    assert 'msg' in data