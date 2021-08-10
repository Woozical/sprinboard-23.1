"""Blogly application."""

from flask import Flask, redirect, render_template, request, flash
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

@app.route('/users/new', methods=['GET'])
def create_form_view():
    return render_template('create-form.html')

@app.route('/users/new', methods=['POST'])
def submit_create_form():
    first_name = request.form['first-name']
    last_name = request.form['last-name']
    image_url = request.form['image-url'] if request.form['image-url'] else None

    if first_name and last_name:
        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/users')
    else:
        if not first_name:
            flash('Missing information in field "First Name"')
        if not last_name:
            flash('Missing information in field "Last Name"')
        return redirect('/create')

@app.route('/users/<int:user_id>')
def user_detail_view(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user-details.html', user=user)