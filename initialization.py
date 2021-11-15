from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from functools import wraps
from flask import redirect, url_for
from flask_login import current_user

db = SQLAlchemy()
DB_NAME = 'database.db'


def deny_basic(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated == False:
            return redirect(url_for('auth.login'))
        elif (current_user.is_admin == False) and (current_user.is_authenticated == True):
            return redirect(url_for('views.home'))
        return f(*args, **kwargs)
    return wrapped


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    from views import views
    from auth import auth
    from streaming import streaming

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(streaming, url_prefix='/')

    from modeldec import User, Note

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    create_database(app)

    return app

def create_database(app):
    if not os.path.exists(DB_NAME):
        with app.app_context():
            db.create_all(app=app)
            print('Created Database!')
        
    else: #TODO: remove this part
        from modeldec import User
        from werkzeug.security import generate_password_hash
        os.remove(DB_NAME)
        with app.app_context():
            db.create_all(app=app)
            new_user = User(email="csokviktor@gmail.com",
                                first_name="csokviktor",
                                password=generate_password_hash("csokiviki", method='sha256'),
                                is_admin=True,
                                is_main_admin=True)
            db.session.add(new_user)
            db.session.commit()