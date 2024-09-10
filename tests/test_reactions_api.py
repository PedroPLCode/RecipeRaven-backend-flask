import pytest
from unittest.mock import patch
from app import create_app, db
from app.models import User, News, Reaction
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('testing')
    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    db.create_all()

    # Dodanie przykładowych danych do bazy
    user = User(login="testuser", email="testuser@example.com", password="testpassword")
    news = News(title="Test News", content="Test content", user_id=1)
    reaction = Reaction(news_id=1, content="Test reaction", user_id=1)

    db.session.add(user)
    db.session.add(news)
    db.session.add(reaction)
    db.session.commit()

    yield testing_client

    db.drop_all()
    ctx.pop()

# Test tworzenia nowej reakcji z mockowaniem wysyłania e-maila
@patch('app.utils.send_email')  # Patchujemy funkcję send_email w module, gdzie jest używana
def test_create_reaction(mock_send_email, test_client):
    access_token = create_access_token(identity="testuser")

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    data = {
        "news_id": 1,
        "content": "New test reaction",
        "guest_author": "Guest User"
    }

    response = test_client.post('/api/reactions', json=data, headers=headers)
    
    # Sprawdzamy, czy funkcja send_email została wywołana
    mock_send_email.assert_called_once()
    
    # Sprawdzamy argumenty, z jakimi została wywołana funkcja
    assert mock_send_email.call_args[0][0] == "testuser@example.com"  # adres e-mail
    assert "RecipeRavenApp" in mock_send_email.call_args[0][1]  # temat wiadomości
    assert "New test reaction" in mock_send_email.call_args[0][2]  # treść wiadomości

    assert response.status_code == 201
    assert response.json['message'] == "Reaction created successfully"


# Test pobierania reakcji (GET)
def test_get_reactions(test_client):
    response = test_client.get('/api/reactions')
    assert response.status_code == 200
    assert len(response.json) > 0
    assert response.json[0]['content'] == "Test reaction"

# Test tworzenia nowej reakcji (POST)
def test_create_reaction(test_client):
    access_token = create_access_token(identity="testuser")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    data = {
        "news_id": 1,
        "content": "New test reaction",
        "guest_author": "Guest User"
    }

    response = test_client.post('/api/reactions', json=data, headers=headers)
    assert response.status_code == 201
    assert response.json['message'] == "Reaction created successfully"

# Test aktualizacji reakcji (PUT)
def test_update_reaction(test_client):
    access_token = create_access_token(identity="testuser")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    data = {
        "content": "Updated test reaction"
    }

    response = test_client.put('/api/reactions/1', json=data, headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == "Reaction updated successfully"

# Test usuwania reakcji (DELETE)
def test_delete_reaction(test_client):
    access_token = create_access_token(identity="testuser")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = test_client.delete('/api/reactions/1', headers=headers)
    assert response.status_code == 200
    assert response.json['msg'] == "Reaction deleted successfully."