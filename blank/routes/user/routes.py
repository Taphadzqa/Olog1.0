# Imports
from flask import render_template, Blueprint, url_for, request, flash, redirect, Markup
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from blank.routes.user.utils import *
from blank.routes.user.forms import *
from blank.core.models import User, Company
from blank import db, bcrypt
import datetime
# Create blueprint handler
user = Blueprint('user', __name__)


# Signin route
@user.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main.browse'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            flash('We experienced an internal error. Please try again.\n\n' + error, 'blue')
        else:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if user.last_login == None:
                    flash('You can change your password in ACCOUNT SETTINGS.', 'blue')
                    current_user.last_login = datetime.datetime.now()
                else:
                    current_user.last_login = datetime.datetime.now()
                db.session.commit()
                return redirect(next_page) if next_page else redirect(url_for('main.browse'))
            else:
                flash('You have provided an invalid email and/or password. Please try again.', 'red')
    return render_template('user/signin.html', title='Sign in', form=form)


# Request token route
@user.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        flash('Go to your settings if you want to change your password.', 'blue')
        return redirect(url_for('main.browse'))
    form = RequestResetForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            flash('We experienced an internal error. Please try again.\n\n' + error, 'blue')
        if user:
            sendResetEmail(user)
            flash('An email has been sent with instructions to reset your password', 'green')
            return redirect(url_for('user.signin'))
        else:
            flash('Email you provided is not registered.', 'red')
            flash(Markup('<a href="{{ url_for("main.contact") }}">Contact the System Administrator</a> to verify your account.'), 'blue')
    return render_template('user/reset_request.html', title='Reset Password', form=form)


# Change password route
@user.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        flash('Go to your settings if you want to change your password.', 'blue')
        return redirect(url_for('main.browse'))
    try:
        user = User.verify_reset_token(token)
    except Exception as e:
        raise
    else:
        if user is None:
            flash('The token you are trying to use is either invalid or it has expired.', 'red')
            return redirect(url_for('user.reset_request'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            user.password = hashed_password
            db.session.commit()
            flash(f'Your password has been updated! You can now login', 'green')
            return redirect(url_for('user.signin'))
    return render_template('user/reset_token.html', title='Reset Password', form=form)



# System users route
@user.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.employer.type != 'Internal':
        return redirect(url_for('main.home'))

    form = RegisterUserForm()
    form.company.choices = getCompanies()
    page = request.args.get('page', 1, type=int)

    try:
        users = User.query.order_by(User.name).paginate(page=page, per_page=25)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        flash('We experienced an internal error. Please try again.\n\n' + error, 'blue')
        return redirect(url_for('main.dashboard'))

    if form.validate_on_submit():
        if addUser(form.name.data, form.email.data, form.role.data, form.status.data, form.company.data):
            flash(form.name.data + ' has been added successfully. An email with the password has been sent to ' + form.email.data, 'green')
        return redirect(url_for('user.users'))

    return render_template('user/users.html', title='System Users', users=users, form=form)



# Profile route
@user.route("/profile")
@login_required
def profile():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated!', 'green')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', title=current_user.name, form=form)


# Sign out route
@user.route("/signout")
def signout():
    logout_user()
    return redirect(url_for('user.signin'))
