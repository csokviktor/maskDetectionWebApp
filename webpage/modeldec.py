from initialization import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    is_main_admin = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(10000), unique=True)
    port = db.Column(db.String(10000))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime(timezone=True))
    cameraID = db.Column(db.Integer)
    resolution = db.Column(db.String(10000))