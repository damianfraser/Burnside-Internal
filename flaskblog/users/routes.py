from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

#Register
@users.route("/register", methods=['GET', 'POST'])
def register():
    #If there is a user you will be taken to the home page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    #Creating the user and hashing the password
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user= User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        #The account has been made
        flash('Your account has been created! You are now able to login!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

#Login
@users.route("/login", methods=['GET', 'POST'])
def login():
    #If there is a user you will be taken to the home page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    #If the email and password is correct you will be able to login and redirected to home page
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            #The email or password was incorrect
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

#Logout
@users.route("/logout")
def logout():
    logout_user()
    #The user is logged out
    return redirect(url_for('main.home'))

#Update Account
@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        #Changing the account, either profile picture, email, or password
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        #The account has been updated
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',title='Account', image_file=image_file, form=form)

#Making the pages
@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5) #Making only 5 posts per page
    return render_template('user_posts.html', posts=posts, user=user)

#Forgot password
@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    #Redirected to home page if you are logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        #An email has been sent to the email address
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

#Reset the password
@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        #If the user is logged in
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if User is None:
        #If it has taken too long for the user to use the email
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        #Hashing the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        #New password has been set
        flash('Your password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)