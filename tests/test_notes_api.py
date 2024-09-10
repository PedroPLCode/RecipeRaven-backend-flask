import pytest
from unittest.mock import patch, MagicMock
from app import app, db
from app.models import Note
from flask_jwt_extended import create_access_token
from app import create_app, db

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def auth_header():
    with app.app_context():
        access_token = create_access_token(identity='testuser')
        return {'Authorization': f'Bearer {access_token}'}


# Testowanie POST dla /api/notes (tworzenie notatki)
@patch('app.models.Note.query.filter_by')
@patch('app.db.session.add')
@patch('app.db.session.commit')
def test_create_note_add(mock_commit, mock_add, mock_filter_by, client, auth_header):
    # Mockowanie filtracji, aby zwrócić None (brak istniejącej notatki)
    mock_filter_by.return_value.first.return_value = None

    response = client.post('/api/notes', json={
        'favorite_id': 1,
        'content': 'This is a new note'
    }, headers=auth_header)

    assert response.status_code == 201
    assert response.headers['Location'] == '/notes/None'  # Nowa notatka

# Testowanie POST dla /api/notes (aktualizowanie istniejącej notatki)
@patch('app.models.Note.query.filter_by')
@patch('app.db.session.commit')
@patch('app.db.session.delete')
def test_create_note_update(mock_delete, mock_commit, mock_filter_by, client, auth_header):
    # Mockowanie istniejącej notatki
    existing_note = MagicMock()
    existing_note.id = 1
    mock_filter_by.return_value.first.return_value = existing_note

    response = client.post('/api/notes', json={
        'favorite_id': 1,
        'content': 'Updated content'
    }, headers=auth_header)

    assert response.status_code == 201
    assert response.headers['Location'] == '/notes/1'

# Testowanie POST dla /api/notes (usuwanie notatki przez ustawienie pustej zawartości)
@patch('app.models.Note.query.filter_by')
@patch('app.db.session.delete')
@patch('app.db.session.commit')
def test_create_note_delete(mock_commit, mock_delete, mock_filter_by, client, auth_header):
    # Mockowanie istniejącej notatki
    existing_note = MagicMock()
    existing_note.id = 1
    mock_filter_by.return_value.first.return_value = existing_note

    response = client.post('/api/notes', json={
        'favorite_id': 1,
        'content': ''
    }, headers=auth_header)

    assert response.status_code == 201
    assert response.headers['Location'] == '/notes/1'

    # Sprawdzanie, czy delete zostało wywołane
    mock_delete.assert_called_once_with(existing_note)

# Testowanie błędnych danych wejściowych
@patch('app.models.Note.query.filter_by')
def test_create_note_no_input(mock_filter_by, client, auth_header):
    response = client.post('/api/notes', json={}, headers=auth_header)
    assert response.status_code == 400
    data = response.get_json()
    assert data['msg'] == 'No input data provided.'