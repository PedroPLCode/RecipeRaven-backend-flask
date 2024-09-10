# tests/test_session_api.py
import pytest
from app import create_app, db
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='module')
def test_client():
    app = create_app('config.TestingConfig')  # Use the correct config object for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Ensure JWT_SECRET_KEY is set

    with app.app_context():
        db.create_all()  # Create all tables in the in-memory database
    
        with app.test_client() as client:
            yield client
    
        db.drop_all()  # Drop all tables after tests
        

def test_create_token(test_client):
    user_data = {
        "login": "testuser",
        "password": "testpassword"
    }

    # Register a new user
    response = test_client.post('/api/users', json=user_data)
    assert response.status_code == 200

    # Attempt to log in
    response = test_client.post('/token', json=user_data)
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_refresh_jwt(test_client):
    access_token = create_access_token(identity="testuser")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = test_client.get('/api/protected', headers=headers)
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_google_oauth(test_client, mocker):
    # Ensure pytest-mock is installed and the 'mocker' fixture is used
    mocker.patch('requests.post', return_value=mocker.Mock(status_code=200, json=lambda: {"access_token": "test_google_token"}))
    mocker.patch('requests.get', return_value=mocker.Mock(status_code=200, json=lambda: {
        "email": "test@google.com",
        "given_name": "Test",
        "name": "Test User",
        "picture": "http://example.com/picture.jpg"
    }))

    response = test_client.post('/google_token', json={'code': 'valid_google_code'})
    assert response.status_code == 200
    assert 'access_token' in response.json