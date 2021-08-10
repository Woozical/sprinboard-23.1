"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DEFAULT_IMG_URL = 'http://www.newdesignfile.com/postpic/2009/09/generic-user-profile_354184.png'


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )

    first_name = db.Column(
        db.String(20), nullable=False
    )

    last_name = db.Column(
        db.String(20), nullable=False
    )

    image_url = db.Column(
        db.String,
        default='no_url'
    )

    def __repr__(self):
        return f'<User ID={self.id} first_name={self.first_name} last_name={self.last_name}>'

    @classmethod
    def get_all(cls):
        return cls.query.all()