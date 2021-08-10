from unittest import TestCase
from app import app
from models import User, db

# Perform tests on a Test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Real Errors
app.config['TESTING'] = True

db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):

    def setUp(self):
        # Clear any leftover entries in DB
        User.query.delete()

        # Create a sample entry
        user = User(first_name="John", last_name="Doe")
        db.session.add(user)
        db.session.commit()

        # Save sample entry's id
        self.user_id = user.id
    
    def tearDown(self):
        # Clear any tainted DB transactions
        db.session.rollback()

    
    def test_directory_view(self):
        with app.test_client() as client:
            res = client.get('/users')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('John Doe', html)

    def test_user_add_view(self):
        with app.test_client() as client:
            res = client.get('/users/new')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<form action="/users/new" method="POST">', html)
    
    def test_user_add_post(self):
        with app.test_client() as client:
            res = client.post('/users/new', data={'first-name':'Jimmy', 'last-name':'Dean', 'image-url': ''}, follow_redirects=True )
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Jimmy Dean', html)

    def test_user_details(self):
        with app.test_client() as client:
            res = client.get(f'/users/{self.user_id}')
            html = res.get_data(as_text=True)
            user = User.query.get(self.user_id)

            self.assertEqual(res.status_code, 200)
            self.assertIn('John Doe', html)
            self.assertIn(f'<img src="{user.image_url}"', html)

    def test_user_edit_post(self):
        with app.test_client() as client:
            data = {'first-name':'James', 'last-name':'Doe', 'image-url':''}
            res = client.post(f'/users/{self.user_id}/edit', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)
            user = User.query.get(self.user_id)

            self.assertEqual(res.status_code, 200)
            self.assertIn('James Doe', html)
            self.assertEqual(user.first_name, 'James')
    
    def test_user_delete_post(self):
        with app.test_client() as client:
            res = client.post(f'/users/{self.user_id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertNotIn('John Doe', html)
            self.assertEqual(User.get_all(), [])