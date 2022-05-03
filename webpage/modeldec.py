from initialization import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    is_main_admin = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))


class Cameras(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(10000))
    port = db.Column(db.String(10000))


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime(timezone=True))
    cameraID = db.Column(db.Integer)
    status = db.Column(db.String(10000))


class SelectedCategories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(10000))
