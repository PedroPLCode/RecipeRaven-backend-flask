import pytest
from unittest.mock import patch
from app import app, db
from app.models import Post, User

# Testowanie zarządzania reakcjami
@patch('app.models.User.query.filter_by')
@patch('app.models.Post.query.filter_by')
@patch('app.models.PostLikeIt.query.filter_by')
@patch('app.models.PostHateIt.query.filter_by')
@patch('app.models.db.session.add')
@patch('app.models.db.session.commit')
@patch('app.models.db.session.delete')
def test_manage_reaction(mock_delete, mock_commit, mock_add, mock_hate_filter, mock_like_filter, mock_post_filter, mock_user_filter, client):
    # Setup mock responses
    mock_user_filter.return_value.first_or_404.return_value = User(id=1, login='test_user')
    mock_post_filter.return_value.first_or_404.return_value = Post(id=1, user_id=2)
    mock_like_filter.return_value.first.return_value = None
    mock_hate_filter.return_value.first.return_value = None

    # Test 'like' action
    response = client.post('/api/posts/like/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['msg'] == 'Like added successfully.'

    # Test removing existing 'like'
    mock_like_filter.return_value.first.return_value = MagicMock()
    response = client.post('/api/posts/like/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['msg'] == 'Like deleted successfully.'

    # Test 'hate' action
    response = client.post('/api/posts/hate/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['msg'] == 'Hate added successfully.'

    # Test removing existing 'hate'
    mock_hate_filter.return_value.first.return_value = MagicMock()
    response = client.post('/api/posts/hate/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['msg'] == 'Hate deleted successfully.'

    # Test invalid action
    response = client.post('/api/posts/invalid_action/1')
    assert response.status_code == 400
    data = response.get_json()
    assert data['msg'] == 'Invalid action.'

    # Test invalid object type
    response = client.post('/api/invalid_type/like/1')
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Invalid object type'