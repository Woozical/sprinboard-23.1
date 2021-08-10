"""Blogly application."""

from flask import Flask, redirect, render_template
from models import db, connect_db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_KEY_HERE'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

@app.route('/')
def home_view():
    return redirect('/users')

@app.route('/users')
def user_list_view():
    users = User.get_all()
    return render_template('list.html', users=users)