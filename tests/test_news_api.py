import pytest
from unittest.mock import patch, MagicMock
from app import app, db
from app.models import User, Post, Comment, PostLikeIt, PostHateIt, Reaction, News, NewsLikeIt, NewsHateIt, CommentLikeIt, CommentHateIt
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_header():
    access_token = create_access_token(identity='test_user')
    return {'Authorization': f'Bearer {access_token}'}

# Testy dla /api/news
@patch('app.models.News.query.all')
@patch('app.utils.process_post_news')
def test_get_news(mock_process_post_news, mock_query_all, client):
    # Mockowanie zwracania listy wiadomości
    mock_news = [MagicMock(), MagicMock()]
    mock_query_all.return_value = mock_news
    mock_process_post_news.return_value = {'title': 'Test News', 'content': 'This is a test news'}

    response = client.get('/api/news')
    assert response.status_code == 200
    assert len(response.json) == len(mock_news)
    assert response.json[0]['title'] == 'Test News'

@patch('app.models.User.query.filter_by')
@patch('app.models.db.session.add')
@patch('app.models.db.session.commit')
def test_create_news(mock_commit, mock_add, mock_filter_by, client, auth_header):
    # Mockowanie użytkownika
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    response = client.post('/api/news', json={
        'title': 'New News Title',
        'content': 'This is the content of the new news'
    }, headers=auth_header)

    assert response.status_code == 201
    assert response.json['msg'] == 'News created successfully.'
    assert response.headers['Location'] == '/posts/None'

@patch('app.models.User.query.filter_by')
@patch('app.models.News.query.filter')
@patch('app.models.db.session.commit')
def test_update_news(mock_commit, mock_query_filter, mock_filter_by, client, auth_header):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    mock_news = MagicMock()
    mock_news.id = 1
    mock_query_filter.return_value.first_or_404.return_value = mock_news

    response = client.put('/api/news/1', json={
        'title': 'Updated News Title',
        'content': 'Updated content'
    }, headers=auth_header)

    assert response.status_code == 200
    assert response.json['msg'] == 'News updated successfully.'
    assert response.headers['Location'] == '/posts/1'

@patch('app.models.User.query.filter_by')
@patch('app.models.News.query.filter')
@patch('app.models.Reaction.query.filter')
@patch('app.models.db.session.delete')
@patch('app.models.db.session.commit')
def test_delete_news(mock_commit, mock_delete, mock_reaction_filter, mock_query_filter, mock_filter_by, client, auth_header):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    mock_news = MagicMock()
    mock_news.id = 1
    mock_query_filter.return_value.first_or_404.return_value = mock_news

    mock_reaction = MagicMock()
    mock_reaction.query.filter.return_value.first.return_value = None

    response = client.delete('/api/news/1', headers=auth_header)

    assert response.status_code == 200
    assert response.json == mock_news

@patch('app.models.User.query.filter_by')
@patch('app.models.News.query.filter')
@patch('app.models.Reaction.query.filter')
def test_delete_news_with_reactions(mock_reaction_filter, mock_query_filter, mock_filter_by, client, auth_header):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    mock_news = MagicMock()
    mock_news.id = 1
    mock_query_filter.return_value.first_or_404.return_value = mock_news

    mock_reaction_filter.return_value.first.return_value = MagicMock()

    response = client.delete('/api/news/1', headers=auth_header)

    assert response.status_code == 400
    assert response.json['msg'] == 'News still have reactions. Cant delete.'

# Testy dla /api/posts
@patch('app.models.Post.query.all')
@patch('app.utils.process_post_news')
def test_get_posts(mock_process_post_news, mock_query_all, client):
    mock_posts = [MagicMock(), MagicMock()]
    mock_query_all.return_value = mock_posts
    mock_process_post_news.return_value = {'title': 'Test Post', 'content': 'This is a test post'}

    response = client.get('/api/posts')
    assert response.status_code == 200
    assert len(response.json) == len(mock_posts)
    assert response.json[0]['title'] == 'Test Post'

@patch('app.models.User.query.filter_by')
@patch('app.models.db.session.add')
@patch('app.models.db.session.commit')
def test_create_post(mock_commit, mock_add, mock_filter_by, client, auth_header):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    response = client.post('/api/posts', json={
        'title': 'New Post Title',
        'content': 'This is the content of the new post'
    }, headers=auth_header)

    assert response.status_code == 201
    assert response.json['msg'] == 'Post created successfully.'
    assert response.headers['Location'] == '/posts/None'

@patch('app.models.User.query.filter_by')
@patch('app.models.Post.query.filter')
@patch('app.models.db.session.commit')
def test_update_post(mock_commit, mock_query_filter, mock_filter_by, client, auth_header):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    mock_post = MagicMock()
    mock_post.id = 1
    mock_query_filter.return_value.first_or_404.return_value = mock_post

    response = client.put('/api/posts/1', json={
        'title': 'Updated Post Title',
        'content': 'Updated content'
    }, headers=auth_header)

    assert response.status_code == 200
    assert response.json['msg'] == 'Post updated successfully.'
    assert response.headers['Location'] == '/posts/1'

@patch('app.models.User.query.filter_by')
@patch('app.models.Post.query.filter')
@patch('app.models.Comment.query.filter')
@patch('app.models.db.session.delete')
@patch('app.models.db.session.commit')
def test_delete_post(mock_commit, mock_delete, mock_comment_filter, mock_query_filter, mock_filter_by, client, auth_header):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    mock_post = MagicMock()
    mock_post.id = 1
    mock_query_filter.return_value.first_or_404.return_value = mock_post

    mock_comment_filter.return_value.first.return_value = None

    response = client.delete('/api/posts/1', headers=auth_header)

    assert response.status_code == 200
    assert response.json == mock_post

@patch('app.models.User.query.filter_by')
@patch('app.models.Post.query.filter')
@patch('app.models.Comment.query.filter')
def test_delete_post_with_comments(mock_comment_filter, mock_query_filter, mock_filter_by, client, auth_header):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    mock_post = MagicMock()
    mock_post.id = 1
    mock_query_filter.return_value.first_or_404.return_value = mock_post

    mock_comment_filter.return_value.first.return_value = MagicMock()

    response = client.delete('/api/posts/1', headers=auth_header)

    assert response.status_code == 400
    assert response.json['msg'] == 'Post still have comments. Cant delete.'

# Testy dla /api/<string:object_type>/<string:action>/<int:object_id>
@patch('app.models.User.query.filter_by')
@patch('app.models.Post.query.filter_by')
@patch('app.models.PostLikeIt.query.filter_by')
@patch('app.models.PostHateIt.query.filter_by')
@patch('app.models.db.session.add')
@patch('app.models.db.session.delete')
@patch('app.models.db.session.commit')
def test_manage_reaction_like(mock_commit, mock_delete, mock_add, mock_hate_filter_by, mock_like_filter_by, mock_query_filter_by, mock_filter_by, client, auth_header):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    mock_post = MagicMock()
    mock_post.id = 1
    mock_query_filter_by.return_value.first_or_404.return_value = mock_post

    mock_like_filter_by.return_value.first.return_value = None
    mock_hate_filter_by.return_value.first.return_value = None

    response = client.post('/api/posts/like/1', headers=auth_header)

    assert response.status_code == 200
    assert response.json['msg'] == 'Reaction added.'

@patch('app.models.User.query.filter_by')
@patch('app.models.Post.query.filter_by')
@patch('app.models.PostLikeIt.query.filter_by')
@patch('app.models.PostHateIt.query.filter_by')
@patch('app.models.db.session.add')
@patch('app.models.db.session.delete')
@patch('app.models.db.session.commit')
def test_manage_reaction_hate(mock_commit, mock_delete, mock_add, mock_hate_filter_by, mock_like_filter_by, mock_query_filter_by, mock_filter_by, client, auth_header):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_filter_by.return_value.first_or_404.return_value = mock_user

    mock_post = MagicMock()
    mock_post.id = 1
    mock_query_filter_by.return_value.first_or_404.return_value = mock_post

    mock_like_filter_by.return_value.first.return_value = None
    mock_hate_filter_by.return_value.first.return_value = None

    response = client.post('/api/posts/hate/1', headers=auth_header)

    assert response.status_code == 200
    assert response.json['msg'] == 'Reaction added.'

if __name__ == '__main__':
    pytest.main()
