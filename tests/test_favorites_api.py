import unittest
from unittest.mock import patch, MagicMock
from app import app, db
from app.models import User, Favorite, Note
from flask_jwt_extended import create_access_token

class FavoritesRoutesTestCase(unittest.TestCase):
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

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    @patch('requests.get')
    def test_create_favorite(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'test image content'
        
        response = self.client.post('/api/favorites', json={
            'data': {
                'calories': '200',
                'image_REGULAR_url': 'http://example.com/image.jpg'
            }
        }, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('location', response.headers)

    @patch('app.models.Favorite.query.filter_by')
    def test_get_favorites(self, mock_filter_by):
        mock_filter_by.return_value.all.return_value = [
            Favorite(data={'calories': '200'}, user_id=self.user.id, starred=False)
        ]
        mock_note = MagicMock()
        mock_note.to_dict.return_value = {'content': 'Test note'}
        
        with patch('app.models.Note.query.filter_by', return_value=MagicMock(first=MagicMock(return_value=mock_note))):
            response = self.client.get('/api/favorites', headers={'Authorization': f'Bearer {self.token}'})
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.json, list)

    @patch('app.models.Favorite.query.filter_by')
    @patch('app.models.Note.query.filter_by')
    def test_delete_favorite(self, mock_note_filter_by, mock_favorite_filter_by):
        favorite = Favorite(data={'calories': '200'}, user_id=self.user.id, starred=False)
        mock_favorite_filter_by.return_value.first_or_404.return_value = favorite
        
        note = Note()
        mock_note_filter_by.return_value.first.return_value = note
        
        with patch('os.path.exists', return_value=True), patch('os.remove'):
            response = self.client.delete(f'/api/favorites/{favorite.id}', headers={'Authorization': f'Bearer {self.token}'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('msg', response.json)

    @patch('app.models.Favorite.query.filter_by')
    def test_handle_starred_favorite(self, mock_filter_by):
        favorite = Favorite(data={'calories': '200'}, user_id=self.user.id, starred=False)
        mock_filter_by.return_value.first_or_404.return_value = favorite
        
        response = self.client.post(f'/api/favorites/starred/{favorite.id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['favorite']['starred'])

        # Toggle the star state
        response = self.client.post(f'/api/favorites/starred/{favorite.id}', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json['favorite']['starred'])

if __name__ == '__main__':
    unittest.main()