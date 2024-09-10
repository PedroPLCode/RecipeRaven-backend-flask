import pytest
from app import app, db
from app.models import User
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user():
    user = User(login="testuser", password="password", email="testuser@example.com")
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(client, user):
    token = create_access_token(identity=user.login)
    return {'Authorization': f'Bearer {token}'}


# Test: Create a new user
def test_create_user(client):
    response = client.post('/api/users', data={
        'login': 'newuser',
        'password': 'newpassword',
        'email': 'newuser@example.com',
        'name': 'New User',
        'about': 'This is a new user'
    })
    assert response.status_code == 200
    assert 'reset_url' in response.json


# Test: Check user by login
def test_check_user_login(client, user):
    response = client.get('/api/check_user/', query_string={'login': 'testuser'})
    assert response.status_code == 200
    assert response.json['login_status'] == True


# Test: Check user by email
def test_check_user_email(client, user):
    response = client.get('/api/check_user/', query_string={'email': 'testuser@example.com'})
    assert response.status_code == 200
    assert response.json['email_status'] == True


# Test: Get user details
def test_get_user(client, user):
    headers = authenticate_user(client, user)
    response = client.get('/api/users', headers=headers)
    assert response.status_code == 200
    assert response.json['user_data']['login'] == 'testuser'


# Test: Check user password
def test_check_user_password(client, user):
    headers = authenticate_user(client, user)
    response = client.post('/api/userpasswdcheck', headers=headers, json={'password': 'password'})
    assert response.status_code == 200
    assert response.json['passwd_check'] == True


# Test: Update user
def test_change_user(client, user):
    headers = authenticate_user(client, user)
    response = client.put('/api/users', headers=headers, data={
        'name': 'Updated Name',
        'about': 'Updated about section'
    })
    assert response.status_code == 200
    assert 'User details updated successfully.' in response.json['msg']


# Test: Delete user
def test_delete_user(client, user):
    headers = authenticate_user(client, user)
    response = client.delete('/api/users', headers=headers)
    assert response.status_code == 200
    assert response.json['name'] == user.name


# Test: Reset password request
def test_reset_password_request(client, user):
    response = client.post('/api/resetpassword', json={'email': 'testuser@example.com'})
    assert response.status_code == 200
    assert 'reset_url' in response.json


# Test: Confirm user email
def test_confirm_user_email(client, user):
    from app import serializer
    token = serializer.dumps(user.email, salt='confirm-email')
    response = client.post(f'/api/user/confirm/{token}')
    assert response.status_code == 201
    assert 'User email confirmed successfully' in response.json['msg']