import os
import sys
import secrets
import cx_Oracle
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskpost import app, db, Bcrypt
from flaskpost.forms import RegistrationForm, LoginForm, UpdateAccountForm, CommentForm
from flaskpost.models import User, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from datetime import date

# users = db.Table('users', db.metadata, autoload=True, autoload_with=db.engine)
# comments = db.Table('comments', db.metadata, autoload=True, autoload_with=db.engine)
series = db.Table('series', db.metadata, autoload=True, autoload_with=db.engine)

connection = cx_Oracle.connect("OTB", "omar2001", "localhost:1521/xe", encoding="UTF-8")
cursor = connection.cursor()


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(series).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@app.route('/register', methods=['GET', 'POST']) 
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account has been created. You can log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST']) 
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('You are not signed in. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout') 
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/posts') 
def posts():
    page = request.args.get('page', 1, type=int)
    posts = db.session.query(series).paginate(page=page, per_page=5)
    return render_template('posts.html', title='All series', posts=posts)

@app.route('/post/<int:id>', methods=['GET', 'POST']) 
def post(id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user.username, series_id=id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment was published', 'success')
        return redirect(url_for('posts'))
    comments = Comment.query.filter_by(series_id=id).all()
    post = db.session.query(series).filter_by(series_id=id).first()
    return render_template('post.html', post=post, form=form, comments=comments)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_imgs', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_imgs/default.jpg')
    comments = comments = Comment.query.filter_by(author=current_user.username).all()
    return render_template('profile.html', title='Profile', image_file=image_file, form=form, comments=comments)

@app.route("/comment/<int:comment_id>/update", methods=['GET', 'POST'])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()
        flash('Your comment was updated', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.content.data = comment.content
    return render_template('update_comment.html', title="Update Comment", form=form, comment=comment)

@app.route("/comment/<int:comment_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('profile'))

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == 'POST':
        searching_value = request.form['search'].title()
        returnVal = cursor.callfunc("search_by_name", int, [searching_value])
        return redirect(url_for('post', id=returnVal))
    else: 
        return render_template('posts.html')
