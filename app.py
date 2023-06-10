from flask import Flask, request, redirect, render_template, url_for,flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag,PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'seckey'

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.create_all()


# @app.route('/')
# def root():
#     """Homepage redirects to list of users."""

#     return redirect("/users")
@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('home.html', posts=posts)

##############################################################################
# User route

@app.route('/users')
def users_index():
    """Show a page with info on all users"""

    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)


@app.route('/users/new', methods=["GET"])
def users_new_form():
    """Show a form to create a new user"""

    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def users_new():
    """Handle form submission for creating a new user"""

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show a page with info on a specific user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)



@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Show a form to edit an existing user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    """Handle form submission for updating an existing user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):
    """Handle form submission for deleting an existing user"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")



@app.route('/users/<int:user_id>/posts/new', methods=["GET"])
def posts_new_form(user_id):
    """Show a form to add a new post for the user"""
    tags = Tag.query.all()
    user = User.query.get_or_404(user_id)
    return render_template('posts/new.html', user=user)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """Handle form submission for adding a new post"""

    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    new_post = Post(
        title=request.form['title'],
        content=request.form['content'],
        user=user
    )

    db.session.add(new_post)
    db.session.commit()

    # Fetch the newly created post from the database
    post = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).first()

    # Get the selected tags from the form
    selected_tags = request.form.getlist('tags')

    # Fetch the tag objects from the database based on the selected tags
    selected_tags = Tag.query.filter(Tag.id.in_(selected_tags)).all()

    # Assign the tags to the post
    post.tags = selected_tags

    db.session.commit()

    return redirect(f"/users/{user_id}")



@app.route('/posts/<int:post_id>')
def posts_show(post_id):
    """Show a page with info on a specific post"""
    tags = Tag.query.all()
    post = Post.query.get_or_404(post_id)
    user = post.user
    return render_template('posts/show.html', post=post)


@app.route('/posts/<int:post_id>/edit')
def posts_edit(post_id):
    """Show a form to edit an existing post"""
    tags = Tag.query.all()
    post = Post.query.get_or_404(post_id)
    return render_template('posts/edit.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def posts_update(post_id):
    """Handle form submission for updating an existing post"""
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']
    # Get the selected tags from the form
    tag_ids = request.form.getlist('tags')

    # Query the tags based on the selected IDs
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    # Assign the tags to the post
    post.tags = tags

    db.session.add(post)
    db.session.commit()

    return redirect(f"/posts/{post_id}")


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def posts_destroy(post_id):
    """Handle form submission for deleting an existing post"""

    post = Post.query.get_or_404(post_id)
    user_id = post.user_id

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{user_id}")

@app.route('/posts')
def posts_index():
    """Show a page with info on all posts"""
    tags = Tag.query.all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('posts/index.html', posts=posts)




@app.route('/tags')
def tags_index():
    # Retrieve the tags from the database or define it here
    tags = Tag.query.all()

    # Render the template with the tags
    return render_template('tags/index.html', tags=tags)

# ...

# Route for creating a new tag
@app.route('/tags/new', methods=['GET', 'POST'])
def tags_new():
    if request.method == 'POST':
        # Handle form submission and create the new tag
        # You can access the submitted data using request.form
        # For example:
        # tag_name = request.form['name']
        # Code to create a new tag with the given name
        tag_name = request.form['name']
        new_tag = Tag(name=tag_name)
        db.session.add(new_tag)
        db.session.commit()
        # Redirect to the list of tags
        return redirect(url_for('tags_index'))
    else:
        # Render the new tag form template
        return render_template('tags/new.html')
    
# ...



# Route for listing all tags
@app.route('/tags2')
def tags_list():
    # Code to fetch all tags from the database
    # For example:
    tags = Tag.query.all()

    # Render the template and pass the tags data
    return render_template('tags/list.html', tags=tags)


# Route for editing a tag
@app.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
def tags_edit(tag_id):
    tag = Tag.query.get(tag_id)
    if request.method == 'POST':
        # Handle form submission and update the tag
        # You can access the submitted data using request.form
        # For example:
        tag_name = request.form['name']
        # Code to update the tag with the new name
        if request.method == 'POST':
            tag_name = request.form['name']
            tag.name = tag_name
            db.session.commit()
        # Redirect to the tag show page
        return redirect(url_for('tags_show', tag_id=tag.id))
    else:
        # Render the edit tag form template
        return render_template('tags/edit.html', tag=tag)


# Route for showing a tag
@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    tag = Tag.query.get(tag_id)
    # Render the tag show template
    return render_template('tags/show.html', tag=tag)


@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def tags_delete(tag_id):
    tag = Tag.query.get(tag_id)
    if tag:
        # Delete the tag from the database
        db.session.delete(tag)
        db.session.commit()
        flash('Tag deleted successfully.', 'success')
    else:
        flash('Tag not found.', 'error')
    return redirect(url_for('tags_index'))
