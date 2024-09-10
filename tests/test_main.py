import unittest
from app import app

class ShowInfoRouteTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'testsecret'
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_show_info(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!doctype html>', response.data)
        self.assertIn(b'<title>Receipes Search App</title>', response.data)
        
if __name__ == '__main__':
    unittest.main()