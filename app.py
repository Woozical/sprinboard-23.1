"""Blogly application."""

from flask import Flask, redirect, render_template, request, flash, session
from models import db, connect_db, User, DEFAULT_IMG_URL, Post, Tag, PostTag

FORBIDDEN_TAG_CHARS = [
    "!","@",'#','$','%','^','('
]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_KEY_HERE'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

@app.route('/recent')
def recent_view():
    query = Post.query.order_by(Post.created_at.desc())
    query = query.limit(5)
    posts = query.all()
    return render_template('recent.html', posts=posts)

@app.route('/')
def home_view():
    return redirect('/recent')

@app.route('/users')
def user_list_view():
    users = User.get_all()
    return render_template('list.html', users=users)

@app.route('/tags')
def tag_list_view():
    tags = Tag.get_all()
    return render_template('tag-list.html', tags=tags)

@app.route('/tags/<int:tag_id>')
def tag_detail_view(tag_id):
    tag = Tag.query.get(tag_id)
    return render_template('tag-detail.html', tag=tag)

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
            flash('Missing information in field "First Name"', 'warning')
        if not last_name:
            flash('Missing information in field "Last Name"', 'warning')
        return redirect('/users/new')

@app.route('/users/<int:user_id>')
def user_detail_view(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user-details.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['GET'])
def user_edit_view(user_id):
    user = User.query.get_or_404(user_id)
    image_path = user.image_url if user.image_url != DEFAULT_IMG_URL else ""
    return render_template('edit-form.html', user=user, image_path=image_path)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def submit_edit_form(user_id):
    user = User.query.get(user_id)

    user.first_name = request.form['first-name'] if request.form['first-name'] else user.first_name
    user.last_name = request.form['last-name'] if request.form['last-name'] else user.last_name
    user.image_url = request.form['image-url'] if request.form['image-url'] else DEFAULT_IMG_URL

    db.session.add(user)
    db.session.commit()

    return redirect(f'/users/{user_id}')

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def submit_delete_user(user_id):
    User.query.filter_by(id=user_id).delete()
    db.session.commit()

    return redirect('/users')

@app.route('/posts/<int:post_id>')
def post_view(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/users/<int:user_id>/posts/new', methods=['GET'])
def create_post_view(user_id):
    user = User.query.get_or_404(user_id)
    saved_content = session.get('FAILED_POST_CONTENT', '')
    saved_title = session.get('FAILED_POST_TITLE', '')

    return render_template('create-post-form.html', user=user, saved_content=saved_content, saved_title=saved_title)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def submit_post_form(user_id):
    title = request.form['post-title'] if request.form['post-title'] else ''
    content = request.form['post-content'] if request.form['post-content'] else ''

    if title and content:
        new_post = Post(title=title, content=content, poster_id=user_id)

        if request.form['post-tags']:
            # Clean input
            tag_list = trim_tag_input_string(request.form['post-tags'])
            
            # Append Tags to the Post object
            for tag in create_tags(tag_list):
                new_post.tags.append(tag)
            
        db.session.add(new_post)
        try:
            db.session.commit()
            cookie_post_content() # Clear from session cookie
            return redirect(f'/posts/{new_post.id}')
        except:
            flash('An error occured when saving your post. Please try again later.', 'danger')
            cookie_post_content(title,content)
            db.session.rollback()
            return redirect(f'/users/{user_id}')
    
    else:
        if not title:
            flash('Missing Post Title', 'warning')
        if not content:
            flash('Missing Post Content', 'warning')
        
        cookie_post_content(title, content)
        return redirect(f'/users/{user_id}/posts/new')


@app.route('/posts/<int:post_id>/edit', methods=['GET'])
def post_edit_form_view(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('edit-post-form.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def post_edit_submission(post_id):
    post = Post.query.get(post_id)

    if request.form['post-title']:
        post.title = request.form['post-title']
    else:
        flash('Post titles are required. The previous title was kept.', 'info')

    if request.form['post-content']:
        post.content = request.form['post-content']
    else:
        flash('Post content body is required. Previous post content was kept.', 'info')
        

    # tags
    if not request.form['post-tags']:
        PostTag.query.filter_by(post_id=post_id).delete()
    else:
        tag_list = trim_tag_input_string(request.form['post-tags'])

        # Delete tags from post that are now missing from edit input
        missing_ids = [x[0] for x in db.session.query(Tag.id).filter(Tag.name.notin_(tag_list)).all()]

        PostTag.query.filter((PostTag.post_id == post_id), (PostTag.tag_id.in_(missing_ids))).delete()

        # tag additions
        for tag in create_tags(tag_list):
            post.tags.append(tag)

    db.session.add(post)
    
    try:
        db.session.commit()
    except:
        flash('An error occured when saving your post. Please try again later.', 'danger')
        db.session.rollback()

    return redirect(f'/posts/{post.id}')

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def submit_delete_post(post_id):
    query = Post.query.filter_by(id=post_id)
    user_id = query.first().poster_id
    query.delete()
    db.session.commit()

    return redirect(f'/users/{user_id}')

def cookie_post_content(title='', content=''):
    """ Saves the data for a failed user post to the session cookie. If called without arguments, clears cached data."""
    session['FAILED_POST_TITLE'] = title
    session['FAILED_POST_CONTENT'] = content

def create_tags(tag_names):
    """Accepts a list of strings, each element being a new tag.
    Will search for tags that already exist with that name in the DB
    Returns a list of Tag Model objects"""
    output = []
    existing_tags = db.session.query(Tag.name, Tag).filter(Tag.name.in_(tag_names)).all()
    tag_dict = {}

    # Split list of tuples into two lists
    for name, obj in existing_tags:
        tag_dict[name] = obj
    
    for i in range(len(tag_names)):
        if tag_names[i] in tag_dict.keys():
            output.append( tag_dict[tag_names[i]] )
        else:
            new_tag = Tag(name=tag_names[i])
            output.append(new_tag)

    return output

def trim_tag_input_string(input_str):

    string = "".join(
        [char for char in input_str if char.isalnum() or char == "," or char == " "]
    )
    #lowercase and strip trailing commas and whitespace
    string = string.lower().strip(", ")
    # split each tag
    tag_list = string.split(',')

    # Remove excess whitespace within each tag
    tag_list = [" ".join(tag_list[i].split()) for i in range(len(tag_list))]

    #remove duplicates, remove empty string that may have slipped through
    tag_list = set(tag_list)
    if '' in tag_list: tag_list.remove('')
    tag_list = list(tag_list)
    return tag_list