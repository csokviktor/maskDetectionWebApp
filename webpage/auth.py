from flask import (Blueprint, render_template, request, flash, redirect, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from modeldec import User
from initialization import db
from flask_login import login_user, login_required, logout_user, current_user
from initialization import deny_basic
import os

auth = Blueprint('auth', __name__)


@auth.route('/sign-up', methods=['GET', 'POST'])
@deny_basic
def sign_up():
    os.environ['processingImage'] = 'stop'
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        is_admin = request.form.get('isAdmin')
        is_admin = True if is_admin == 'on' else False

        user = User.query.filter_by(email=email).first()
        if user:
            flash('This email already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # add user to db
            new_user = User(email=email,
                            first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'),
                            is_admin=is_admin,
                            is_main_admin=False)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created.', category='success')
            return redirect(url_for('views.home'))
    else:
        pass
    return render_template("signup.html", user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    os.environ['processingImage'] = 'stop'
    if current_user.is_authenticated == True:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again!', category='error')
        else:
            flash('Email does not exists!', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/edit-user', methods=['GET', 'POST'])
def edit_user():
    os.environ['processingImage'] = 'stop'
    users = User.query.all()
    return render_template('edituser.html', user=current_user, userlist=users)


@auth.route('/logout')
@login_required
def logout():
    os.environ['processingImage'] = 'stop'
    logout_user()
    flash("Logged out successfully.", category='success')
    return redirect(url_for('auth.login'))