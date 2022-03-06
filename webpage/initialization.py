from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from functools import wraps
from flask import redirect, url_for
from flask_login import current_user

import os
import pathlib

db = SQLAlchemy()
DB_NAME = 'database.db'

procList = None
procLock = None

def deny_basic(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated == False:
            return redirect(url_for('auth.login'))
        elif (current_user.is_admin == False) and (current_user.is_authenticated == True):
            return redirect(url_for('views.home'))
        return f(*args, **kwargs)
    return wrapped

def create_app(list = None, lock = None):
    from views import views
    from auth import auth
    from streaming import streaming
    from camerahandling import camerahandling
    from modeldec import User

    global procList
    global procLock

    procList = list
    procLock = lock

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(streaming, url_prefix='/')
    app.register_blueprint(camerahandling, url_prefix='/')    

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    create_database(app)

    return app

def create_database(app):
    db_path = os.path.join(
            pathlib.Path(__file__).parent.resolve(),
            DB_NAME
            )
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all(app=app)
            print('Created Database!')
        
    else: #TODO: remove this part
        from modeldec import User, Cameras
        from werkzeug.security import generate_password_hash
        os.remove(db_path)
        with app.app_context():
            db.create_all(app=app)
            new_user = User(
                email="csokviktor@gmail.com",
                first_name="csokviktor",
                password=generate_password_hash("csokiviki", method='sha256'),
                is_admin=True,
                is_main_admin=True)
            new_camera = Cameras(
                ip = "127.0.0.0",
                port = "5554"
            )
            db.session.add(new_user)
            db.session.add(new_camera)
            db.session.commit()