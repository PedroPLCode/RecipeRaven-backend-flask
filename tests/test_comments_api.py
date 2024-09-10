import unittest
from unittest.mock import patch, MagicMock
from app import app, db
from app.models import User, Comment, Post
from flask_jwt_extended import create_access_token

class CommentsRoutesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test user and generate a JWT token
        self.user = User(login='testuser', password='password')
        db.session.add(self.user)
        db.session.commit()
        self.token = create_access_token(identity=self.user.login)
        
        self.post = Post(title='Test Post', content='Content of the post', user_id=self.user.id)
        db.session.add(self.post)
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    @patch('app.models.Comment.query.all')
    def test_get_comments(self, mock_all):
        mock_all.return_value = [
            Comment(content='This is a comment', post_id=self.post.id, user_id=self.user.id)
        ]
        
        response = self.client.get('/api/comments')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['content'], 'This is a comment')

    @patch('app.models.User.query.filter_by')
    @patch('app.models.Post.query.filter_by')
    @patch('app.models.Comment')
    @patch('app.utils.send_email')
    def test_create_comment(self, mock_send_email, mock_comment, mock_post_filter_by, mock_user_filter_by):
        mock_user_filter_by.return_value.first_or_404.return_value = self.user
        mock_post_filter_by.return_value.first_or_404.return_value = self.post
        mock_comment.return_value = MagicMock(id=1, content='New comment')
        mock_comment.query = MagicMock()
        mock_comment.query.filter_by.return_value = mock_comment

        response = self.client.post('/api/comments', json={
            'post_id': self.post.id,
            'content': 'New comment'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('location', response.headers)
        mock_send_email.assert_called_once()

    @patch('app.models.Comment.query.filter')
    @patch('app.models.User.query.filter_by')
    def test_update_comment(self, mock_user_filter_by, mock_comment_filter):
        comment = Comment(content='Old content', post_id=self.post.id, user_id=self.user.id)
        db.session.add(comment)
        db.session.commit()
        
        mock_user_filter_by.return_value.first_or_404.return_value = self.user
        mock_comment_filter.return_value.first_or_404.return_value = comment

        response = self.client.put(f'/api/comments/{comment.id}', json={
            'content': 'Updated content'
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.content, 'Updated content')

    @patch('app.models.Comment.query.filter')
    @patch('app.models.User.query.filter_by')
    def test_delete_comment(self, mock_user_filter_by, mock_comment_filter):
        comment = Comment(content='To be deleted', post_id=self.post.id, user_id=self.user.id)
        db.session.add(comment)
        db.session.commit()
        
        mock_user_filter_by.return_value.first_or_404.return_value = self.user
        mock_comment_filter.return_value.first_or_404.return_value = comment
        
        response = self.client.delete(f'/api/comments/{comment.id}', headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['msg'], 'Comment deleted successfully.')

if __name__ == '__main__':
    unittest.main()