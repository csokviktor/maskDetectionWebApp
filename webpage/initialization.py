import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from functools import wraps
from flask import redirect, url_for
from flask_login import current_user
from parallelDetect import runSubscriber

import os
import pathlib
import threading

db = SQLAlchemy()
DB_NAME = 'database.db'

inpDict = None
inpLock = None
procDict = None
procLock = None
tasks = dict()

available_categories = list()


def deny_basic(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        elif (current_user.is_admin == False) and (current_user.is_authenticated == True):
            return redirect(url_for('views.home'))
        return f(*args, **kwargs)

    return wrapped


def create_app(
        inputDict=None, inputLock=None,
        processedDict=None, processedLock=None):
    from views import views
    from auth import auth
    from streaming import streaming
    from camerahandling import camerahandling
    from notification import notification
    from modeldec import User, Cameras, SelectedCategories
    global inpDict
    global inpLock
    global procDict
    global procLock
    global available_categories

    inpDict = inputDict
    inpLock = inputLock
    procDict = processedDict
    procLock = processedLock

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    db.init_app(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(streaming, url_prefix='/')
    app.register_blueprint(camerahandling, url_prefix='/')
    app.register_blueprint(notification, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    with open("./webpage/categories.json", mode='r', encoding='utf-8') as fp:
        available_categories = json.load(fp).get('available_categories')

    create_database(app, User, Cameras, SelectedCategories)
    init_cameras(app, Cameras)
    return app


def create_database(app, user, cameras, selectedcats):
    db_path = os.path.join(
        pathlib.Path(__file__).parent.resolve(),
        DB_NAME
    )
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all(app=app)
            print('Created Database!')

    else:  # TODO: remove this part
        from werkzeug.security import generate_password_hash
        os.remove(db_path)
        with app.app_context():
            db.create_all(app=app)
            new_user = user(
                email="csokviktor@gmail.com",
                first_name="csokviktor",
                password=generate_password_hash("csokiviki", method='sha256'),
                is_admin=True,
                is_main_admin=True)
            new_camera = cameras(
                ip="tcp://127.0.0.1",
                port="5554"
            )
            new_category = selectedcats(
                category='demo'
            )
            db.session.add(new_user)
            db.session.add(new_camera)
            db.session.add(new_category)
            db.session.commit()


def init_cameras(app, cameras):
    global tasks
    with app.app_context():
        cams = cameras.query.all()
        for camera in cams:
            ip = f"{camera.ip}:{camera.port}"
            print(camera.id)
            t = threading.Thread(target=runSubscriber, args=(ip, camera.id, inpDict, inpLock))
            t.start()
            tasks[camera.id] = t
