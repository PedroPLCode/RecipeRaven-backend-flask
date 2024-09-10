# tests/test_admin_views.py
import pytest
import json
from flask import url_for
from flask_login import current_user
from werkzeug.security import generate_password_hash
from app import app, db
from app.models import User, Newsletter
from flask_testing import TestCase

class AdminViewsTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()
        # Create a test user
        self.test_user = User(
            email='admin@example.com',
            password_hash=generate_password_hash('password'),
            login='admin'
        )
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_admin_login_success(self):
        response = self.client.post(
            url_for('admin_login'),
            data=dict(email='admin@example.com', password='password'),
            follow_redirects=True
        )
        self.assert200(response)
        self.assertIn(b'Welcome back', response.data)
        self.assertEqual(current_user.email, 'admin@example.com')

    def test_admin_login_failure(self):
        response = self.client.post(
            url_for('admin_login'),
            data=dict(email='admin@example.com', password='wrongpassword'),
            follow_redirects=True
        )
        self.assert200(response)
        self.assertIn(b'Invalid email or password', response.data)

    def test_admin_logout(self):
        # Log in first
        self.client.post(
            url_for('admin_login'),
            data=dict(email='admin@example.com', password='password')
        )
        response = self.client.get(url_for('admin_logout'), follow_redirects=True)
        self.assert200(response)
        self.assertIn(b'Logged out.', response.data)
        #self.assertNotIn(b'Welcome back', response.data)

    def test_admin_newsletter_success(self, mocker):
        # Mock send_email function
        mock_send_email = mocker.patch('app.routes.send_email', autospec=True)

        response = self.client.post(
            url_for('admin_newsletter'),
            data=dict(topic='Test Newsletter', content='This is a test newsletter'),
            follow_redirects=True
        )
        self.assert200(response)
        self.assertIn(b'Newsletter sent to', response.data)
        
        # Check that send_email was called with the correct arguments
        mock_send_email.assert_called_once_with('admin@example.com', 'Test Newsletter', 'This is a test newsletter')
        
        # Check that the newsletter was added to the database
        newsletter = Newsletter.query.first()
        self.assertIsNotNone(newsletter)
        self.assertEqual(newsletter.title, 'Test Newsletter')
        self.assertEqual(newsletter.content, 'This is a test newsletter')

    def test_admin_newsletter_failure(self, mocker):
        # Mock send_email function to raise an exception
        mocker.patch('app.routes.send_email', side_effect=Exception('Email sending failed'))

        response = self.client.post(
            url_for('admin_newsletter'),
            data=dict(topic='Test Newsletter', content='This is a test newsletter'),
            follow_redirects=True
        )
        self.assert200(response)
        self.assertIn(b'Newsletter sent to', response.data)
