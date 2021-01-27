from flask import Flask, request, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import db, connect_db, User, Post, PostTag, Tag
from datetime import datetime
from sqlalchemy import text


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blog_users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'thisIStheKEY'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

#---------------------------Route for login verification-----------

@app.route('/login/<int:user_id>')
def login_info(user_id):
    user = User.query.get(user_id)
    return render_template('login.html', user=user)

@app.route('/login/<int:user_id>', methods=['POST'])
def login(user_id):
    username = request.form['username']
    password = request.form['password']

    user = User.query.get_or_404(user_id)

    if username != user.username or password != user.password:
        flash('Username or Password is wrong, Please try again')
        return redirect(f"/login/{user_id}")
    elif username == user.username and password == user.password:
        return redirect(f"/user/{user_id}")






# --------------------------Route for User information------------------

@app.route('/')
def user_home():
    users = User.query.all()

    tags = Tag.query.all()

    post = Post.query.order_by(text('id desc')).limit(5)

    return render_template('base.html', users=users, tags=tags, posts=post)

@app.route('/', methods=["POST"])
def create_user():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image = request.form["image"]
    image = image if image else None

    username = request.form["username"]
    password = request.form["password"]

    if username == "" or password =="":
        flash('Please enter a Username and Password')
        return redirect("/")
    else:
        new_user = User(first_name=first_name, last_name=last_name, username=username, password=password, image_url=image)

        db.session.add(new_user)
        db.session.commit()


        return redirect(f"/user/{new_user.id}")
    

    

@app.route('/404')
def error_page():
    return render_template('404.html')

@app.route('/user/<int:User_id>')
def user_profile(User_id):
    userId = User.query.get_or_404(User_id)

    posts = Post.query.filter_by(user_id=userId.id).all()

    return render_template('userProfile.html', user=userId, posts=posts)


@app.route('/editUser/<int:user_id>')
def edit_user(user_id):
    user_id = User.query.get_or_404(user_id)
    return render_template('editUser.html', user=user_id)

@app.route('/user/<int:User_id>', methods=["POST"])
def updated_profile(User_id):
    userId = User.query.get_or_404(User_id)
    
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image = request.form["image"]


    User.review_information(userId, first_name, last_name, image)
        
    
    return render_template('userProfile.html', user=userId)

@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    User.delete_user(user)
    return redirect('/')
    

# ---------------------------------Routes for user posts------------------


@app.route('/delete/<int:post_id>/<int:user_id>')
def delete_post(post_id, user_id):
    Post.delete_user_post(post_id)

    user_id = User.query.get(user_id)
    return redirect(f"/user/{user_id.id}")

@app.route('/edit/<int:post_id>/<int:user_id>', methods=['POST'])
def edit_post(post_id, user_id):
    new_title = request.form["title"]
    new_content = request.form["content"]
    edit_tags = request.form.getlist('selected')
    
    Post.edit_user_post(post_id, new_title, new_content, edit_tags)

    user_id = User.query.get(user_id)
    return redirect(f"/user/{user_id.id}")

@app.route('/edit/<int:post_id>/<int:user_id>')
def edit(post_id, user_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    return render_template('editPost.html', post=post, user=user, tags=tags)


@app.route('/newpost/<int:user_id>')
def new_post(user_id):
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    return render_template('newpost.html', user=user, tags=tags)


@app.route('/usersPost/<int:user_id>', methods=["POST"])
def add_post(user_id):
    userId = User.query.get_or_404(user_id)

    date_time = datetime.now()
    date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    
    title = request.form['title']
    content = request.form['content']
    new_tags = request.form.getlist('selected')

    new_post = Post(title=title, content=content, created_at=date_time, user_id=userId.id)

    new_post_title = new_post.title

    db.session.add(new_post)
    db.session.commit()

    PostTag.add_tags(new_post_title, new_tags)
    
    

    return redirect(f"/user/{userId.id}")

# -----------------------Routes for PostTag-----------------

@app.route('/newpost/<int:user_id>', methods=['POST'])
def add_tag(user_id):
    user = User.query.get_or_404(user_id)

    new_tag = request.form['tag']

    tag = Tag(name=new_tag)
    db.session.add(tag)
    db.session.commit()
    
    return redirect(f"/newpost/{user.id}")

@app.route('/removeTag/<int:user_id>/<int:tag_id>')
def remove_tag(user_id, tag_id):
    tag = Tag.query.get(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(f'/newpost/{user_id}')

@app.route('/tag/<int:tag_id>')
def related_tags(tag_id):

    post_tags = PostTag.query.filter_by(tag_id=tag_id).all()

    tags = Tag.query.all()

    posts = []

    for tag in post_tags:
        post = Post.query.get(tag.post_id)
        posts.append(post)

    return render_template('posts.html', posts=posts, tags=tags)