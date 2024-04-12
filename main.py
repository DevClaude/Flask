from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms.webforms import UserForm, LoginForm, NameForm, PasswordForm, PostForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Create a Flask Instances
app = Flask(__name__)

# Add CKEditor
ckeditor = CKEditor(app)

# Secret Key
app.config['SECRET_KEY'] = 'Secret Key'

# Add Database
# SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# MySql DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/users_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# image path folder
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#----------------------- Model -------------------------#
# Create Users Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash  = db.Column(db.String(128), nullable=False)
    profile_pic = db.Column(db.String(128), nullable=True)
    # User Can Have Many Posts
    posts = db.relationship('Posts', backref='user')
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable password!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Create String
    def __repr__(self):
        return '<Name %r>' % self.name

# Create Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))   
    # Foreign Key To Link Users(refer to primary key of the user)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    


	# Filters in Jinja2
	# bold
	# safe
	# capitalize
	# lower
	# upper
	# title
	# trim
	# striptags

# Return Json thing
@app.route('/json')
def json():
    return {
        'John': 'Pepperoni',
        'Mary': 'Cheese',
        'Tim': 'Mushroom'
    }

# Pass Stuff To Navbar
@app.context_processor
def base():
    form= SearchForm()
    return dict(form=form)
    
# Search
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        
        #Query the Database
        posts = Posts.query.filter(Posts.content.like(f'%{post.searched}%'))
        posts = posts.order_by(Posts.title).all()
        
        return render_template(
            'search.html',
            form= form,
            searched= post.searched,
            posts= posts
            )

# Admin
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 8:
        return render_template('admin.html')
    else:
        flash("You don't have access! You must be the admin to access the admin page!")
        return redirect(url_for('dashboard'))

#-------------------------- User Routes ----------------------------    
# Add User on Database Record 
@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        email = Users.query.filter_by(email=form.email.data).first()
        if email is None:
            # Hash the password!!
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2', salt_length=16)
            if request.method == 'POST':
                user = Users(name=form.name.data,user_name=form.user_name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
                form.user_name=''
                name = form.name.data
                form.name.data = ''
                form.email.data = ''
                form.favorite_color = ''
                form.user_name=''
                flash('User Added Successfully!')
    users = Users.query.order_by(Users.date)
    return render_template('add_user.html',
                    form=form,
                    name=name,
                    users = users
				)

# Update User on Datebase Record
@app.route('/user/update/<int:id>', methods=['GET','POST'])
@login_required
def update_user(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        file = request.files['profile_pic']
        
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.favorite_color = request.form['favorite_color']
        user_to_update.user_name = request.form['user_name']
        user_to_update.about_author = request.form['about_author']
        
        form.about_author.data = current_user.about_author
        if file:
            if user_to_update.profile_pic != None:
                os.remove(f'static/images/{user_to_update.profile_pic}')
            # Grab image
            pic_filename = secure_filename(file.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + '_' + pic_filename
            
            user_to_update.profile_pic = pic_name
            
            try:
                db.session.commit()
                # Save The Image
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash('User Updated Successfully!')
                return render_template(
                    'dashboard.html',
                    form=form
                )
            except:
                flash('Error, looks like there was a problem please try again')
                return render_template(
                    'update_user.html',
                    form=form,
                    user_to_update=user_to_update
                )
        else:
            db.session.commit()
            flash('User Updated Successfully!')
            return render_template(
                'dashboard.html',
                form=form
            )
    else:
        return render_template(
				'update_user.html',
				form=form,
				user_to_update=user_to_update,
				id= id
			)

#Delete User on Database Record
@app.route('/user/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    user= Users.query.get_or_404(id)
    name= None
    form= UserForm()
    if current_user.id == user.id:
        try:
            db.session.delete(user)
            db.session.commit()
            flash('User Deleted Successfully!')
            users = Users.query.order_by(Users.date)
            return render_template(
                'add_user.html',
                form= form,
                name= name,
                users= users
                )
        except:
            flash('Whoops! There was a problem deleting the users')
            return render_template(
                'add_user.html',
                form= form,
                name= name,
                users= users
            )
    else:
        flash("Sorry, you can't delete that user!")
        return redirect(url_for('dashboard'))

#-------------------------- Authentication Routes ------------------------
# Flask_Login
login_manager  = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(user_name=form.user_name.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login Successfully!')
                if(user.id == 8):
                    return redirect(url_for(
                    'admin'
                    ))
                else:
                    return redirect(url_for(
                        'dashboard'
                    ))
            else:
                flash('Wrong Password - Try Again')
        else:
            flash("That User Doesn't Exist - Try Again")
    return render_template(
        'login.html',
        form= form
    )

# Logout Page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('login'))
    
# Dashboard Page
@app.route('/dashboard')
@login_required
def dashboard():
    form = UserForm()
    return render_template(
        'dashboard.html',
        form= form
    )

#----------------------- Posts Routes ---------------------------
# Get all Posts
@app.route('/posts')
def posts():
    
    # Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    
    return render_template(
        'posts.html',
        posts = posts
        )

# Get all Posts by user id
# @app.route('/posts')
# @login_required
# def posts():
    
#     # Get all post by user id
#     posts = Posts.query.filter(Posts.user_id == current_user.id)
    
#     return render_template(
#         'posts.html',
#         posts = posts
#         )
    
# Get Post By id
@app.route('/posts/<int:id>')
def post(id):
    
    # Grab the post by id from the database
    post = Posts.query.get_or_404(id)
    return render_template(
        'post.html',
        post= post
    )

# Add Post
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    title = form.title.data
    content = form.content.data
    slug = form.slug.data
    
    if form.validate_on_submit():
        user = current_user.id
        post = Posts(
            title= title, 
            content= content, 
            slug= slug, 
            user_id= user )
        
        # Add post data to database
        db.session.add(post)
        db.session.commit()
        
        # Clear form
        title = ''
        content = ''
        author = ''
        slug = ''
        
        # Return a Message
        flash('Blog Post Created Successfully!')
        
        # go to posts.html or post posts page
        return redirect(url_for('posts'))
    
    return render_template(
        'add_post.html',
        form= form,
        # post= post
    )
    
# Edit Post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post= Posts.query.get_or_404(id)
    form= PostForm()
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        
        # Update post data to database
        try:
            db.session.commit()
            flash('Posts Updated Successfully!')
            return redirect(url_for(
                'post', 
                id=post.id)
                )
        except:
            form.content.data = post.content
            flash('Error! There was a problem updating the post. Please try again later!')
            return render_template(
                'edit_post.html',
                form= form
            )
    form.content.data = post.content
    if current_user.id == post.user_id:
        return render_template(
            'edit_post.html',
            post= post,
            form= form
        )
    else:
        flash("You Aren't Authorize To Edit This Post!")
        # posts = Posts.query.filter(Posts.user_id == current_user.id)
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template(
            'posts.html',
            posts= posts
        )
    
# Delete Post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    # Delete post from the database
    post_to_delete = Posts.query.get_or_404(id)
    user_id = current_user.id
    
    # Grab all posts from the database
    posts= Posts.query.order_by(Posts.date_posted)
    
    if user_id == post_to_delete.user.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post Deleted Successfully!')
            return render_template(
                'posts.html',
                posts= posts
                )
        except:
            flash('Whoops! There was a problem deleting the users')
            return render_template(
                'posts.html',
                posts= posts
            )
    else:
        flash("You Aren't Authorize To Delete That Post!")
        return render_template(
            'posts.html',
            posts= posts
        )

# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        
        # Look up User By Email
        pw_to_check = Users.query.filter_by(email=email).first()
        
        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)
        
        #Clear the form
        form.email.data = ''
        form.password_hash.data = ''
        flash('Form Submitted Successfully!')
    
    return render_template(
        'test_pw.html',
		email= email,
        password= password,
		form= form,
        pw_to_check= pw_to_check,
        passed= passed
        )

# Create a route decorator
@app.route('/')
# def index():
#   return '<h1>Hello World!</h1>'
def index():
	first_name = 'John'
	stuff = 'This is bold text'
	favorite_pizza = ['Pepperonni', 'Cheese', 'Hawaian', 41]
	return render_template('index.html', 
		first_name = first_name,
		stuff = stuff,
		favorite_pizza = favorite_pizza
        )

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', user_name= name)

# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form Submitted Successfully!')
    
    return render_template('name.html',
		name = name,
		form = form)

# Create Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)