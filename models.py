"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy
import datetime

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
        nullable=False,
        default=DEFAULT_IMG_URL
    )

    posts = db.relationship('Post', backref='poster')

    def __repr__(self):
        return f'<User ID={self.id} first_name={self.first_name} last_name={self.last_name}>'

    @classmethod
    def get_all(cls, sorted=True):
        return cls.query.order_by(cls.last_name, cls.first_name).all() if sorted else cls.query.all()
    
    def image_url_is_default(self):
        return self.image_url == DEFAULT_IMG_URL
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )

    title = db.Column(
        db.Text, nullable=False
    )

    content = db.Column(
        db.Text, nullable=False
    )

    created_at = db.Column(
        db.TIMESTAMP, nullable=False,
        default= datetime.datetime.now
    )

    poster_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete="SET NULL")
    )

    def __repr__(self):
        if len(self.title) > 11:
            return f'<Post ID {self.id} "{self.title[:11]}..." {self.created_at}>'
        else:
            return f'<Post ID {self.id} "{self.title} {self.created_at}>'

    @property
    def create_date(self):
        """Returns a string in a date format (e.g. Aug 10, 2011)"""
        return self.created_at.strftime("%B %d, %Y")

    @property
    def tags_as_string(self):
        output = ""
        if self.tags:
            for tag in self.tags:
                output = output + tag.name + ", "
        
        return output.rstrip(", ")

class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )

    name = db.Column(
        db.String(12), nullable=False, unique=True
    )

    posts = db.relationship('Post', secondary='posts_tags', backref='tags')

    def __repr__(self):
        return f"<Tag ID{self.id} {self.name}>"

    @classmethod
    def get_all(cls, sorted=True):
        return cls.query.order_by(cls.name).all() if sorted else cls.query.all()

    @property
    def post_count(self):
        return len(self.posts)

class PostTag(db.Model):
    __tablename__ = "posts_tags"

    post_id = db.Column(
        db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )

    tag_id = db.Column(
        db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

