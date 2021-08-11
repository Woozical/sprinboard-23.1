from unittest import TestCase
from app import app
from models import User, db, Post

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
        Post.query.delete()
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
            self.assertIn('<form action="/users/new" method="POST"', html)
    
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


class PostViewsTestCase(TestCase):
    def setUp(self):
        # Clear leftover entries
        Post.query.delete()
        User.query.delete()
        # New sample entries
        user = User(first_name="John", last_name="Doe")
        db.session.add(user)
        db.session.commit()

        post = Post(title="Day at the Zoo", content="Lorem ipsum dolor", poster_id = user.id)
        db.session.add(post)
        db.session.commit()

        # Cache IDs
        self.post_id = post.id
        self.user_id = user.id

    def tearDown(self):
        db.session.rollback()


    def test_new_post_form_view(self):
        with app.test_client() as client:
            res = client.get(f'/users/{self.user_id}/posts/new')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'form action="/users/{self.user_id}/posts/new" method="POST"', html)
            self.assertIn('<h1>Add Post for John Doe</h1>', html)

    def test_new_post_submission(self):
        with app.test_client() as client:
            data = {'post-title': 'My Newest Post', 'post-content': 'Ladee-da-dee-dah'}
            res = client.post(f'/users/{self.user_id}/posts/new', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('My Newest Post', html)
            self.assertIn('John Doe', html)

            posts = Post.query.filter_by(title='My Newest Post').all()

            self.assertNotEqual(posts, [])

    def test_failed_new_post_submisssion(self):
        with app.test_client() as client:
            data = {'post-title': '', 'post-content': 'oainrgoairnhae'}
            res = client.post(f'/users/{self.user_id}/posts/new', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('alert', html)

    def test_post_view(self):
        with app.test_client() as client:
            res = client.get(f'/posts/{self.post_id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Day at the Zoo', html)
            self.assertIn('Lorem ipsum dolor', html)
            self.assertIn('John Doe', html)

    def test_post_edit_form_view(self):
        with app.test_client() as client:
            res = client.get(f'/posts/{self.post_id}/edit')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'<form action="/posts/{self.post_id}/edit" method="POST"', html)

    def test_edit_post_submission(self):
        with app.test_client() as client:
            data = {'post-title': 'New Title', 'post-content': 'New Content'}
            res = client.post(f'/posts/{self.post_id}/edit', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('New Title', html)
            self.assertIn('New Content', html)

            post = Post.query.get(self.post_id)
            self.assertEqual(post.title, 'New Title')
            self.assertEqual(post.content, 'New Content')

    def test_failed_edit_submission(self):
        with app.test_client() as client:
            data = {'post-title': '', 'post-content':''}
            res = client.post(f'/posts/{self.post_id}/edit', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Day at the Zoo', html)
            self.assertIn('Lorem ipsum dolor', html)

            post = Post.query.get(self.post_id)

            self.assertEqual(post.title, 'Day at the Zoo')
            self.assertEqual(post.content, 'Lorem ipsum dolor')


    def test_deletion_submission(self):
        with app.test_client() as client:
            res = client.post(f'/posts/{self.post_id}/delete')

            self.assertEqual(res.status_code, 302)
            
            post = Post.query.get(self.post_id)

            self.assertIsNone(post)