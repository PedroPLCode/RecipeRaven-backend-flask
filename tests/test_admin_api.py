# tests/test_admin.py
import pytest
from app import create_app, db
from flask_login import current_user
from flask_jwt_extended import create_access_token
from app.models import User, Newsletter
from werkzeug.security import generate_password_hash
from unittest.mock import patch

@pytest.fixture(scope='module')
def test_client():
    app = create_app('config.TestingConfig')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'

    with app.app_context():
        db.create_all()
        
        # Create a test admin user
        test_user = User(
            login="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("password"),
            role='admin'
        )
        db.session.add(test_user)
        db.session.commit()
        
        with app.test_client() as client:
            yield client
        
        db.drop_all()

def test_admin_login(test_client):
    response = test_client.post('/admin/login', data=dict(email="admin@example.com", password="password"), follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome back admin' in response.data

def test_admin_newsletter(test_client):
    with test_client.session_transaction() as sess:
        sess['_user_id'] = User.query.first().id  # Log in the test user
        
    response = test_client.post('/newsletter', data=dict(topic="Test Newsletter", content="This is a test."), follow_redirects=True)
    assert response.status_code == 200
    assert b'Newsletter sent' in response.data
    assert Newsletter.query.count() == 1

def test_admin_logout(test_client):
    with test_client.session_transaction() as sess:
        sess['_user_id'] = User.query.first().id  # Log in the test user
        
    response = test_client.get('/admin/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged out' in response.data
    assert current_user.is_authenticated is False

def test_admin_newsletter_with_mocking(test_client, mocker):
    mock_send_email = mocker.patch('app.routes.send_email')
    
    with test_client.session_transaction() as sess:
        sess['_user_id'] = User.query.first().id  # Log in the test user
        
    response = test_client.post('/newsletter', data=dict(topic="Test Newsletter", content="This is a test."), follow_redirects=True)
    assert response.status_code == 200
    mock_send_email.assert_called_once()  # Check if send_email was called
