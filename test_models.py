from unittest import TestCase
from app import app
from models import db, User, DEFAULT_IMG_URL

# Perform tests on a Test database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):

    def setUp(self):
        """Delete any leftover database entries"""
        User.query.delete()

    def tearDown(self):
        """Clean up fouled transactions"""
        db.session.rollback()
    
    def test_fullNameProp(self):
        user = User(first_name="John", last_name="Doe")
        self.assertEqual(user.full_name, "John Doe")

    def test_defaultImage(self):
        userOne = User(first_name="John", last_name="Doe")
        userTwo = User(first_name="Jane", last_name="Doe", image_url="https://duckduckgo.com/assets/bathroom.png")
        
        db.session.add(userOne)
        db.session.add(userTwo)
        db.session.commit()

        self.assertEqual(userOne.image_url, DEFAULT_IMG_URL)
        self.assertEqual(userTwo.image_url, "https://duckduckgo.com/assets/bathroom.png")

    def test_sortedQuery(self):
        userOne = User(first_name="John", last_name="Doe")
        userTwo = User(first_name="Jane", last_name="Doe")
        userThree = User(first_name="John", last_name="Fitzgerald")

        db.session.add_all([userOne, userTwo, userThree])
        db.session.commit()

        self.assertEqual(User.get_all(), [userTwo, userOne, userThree])