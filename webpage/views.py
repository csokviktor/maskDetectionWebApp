from flask import (
    Blueprint, render_template,
    request, jsonify)
from flask_login import login_required, current_user
from initialization import deny_basic
from modeldec import User
from initialization import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['POST', 'GET'])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/delete-user', methods=['POST'])
@deny_basic
def delete_user():
    data = json.loads(request.data)
    userID = data['userID']
    user = User.query.get(userID)
    if user:
        db.session.delete(user)
        db.session.commit()

    return jsonify({})


@views.route('/update-user', methods=['POST'])
@deny_basic
def update_user():
    data = json.loads(request.data)
    userID = data['userID']
    user = User.query.get(userID)
    if user:
        user.is_admin = not user.is_admin
        db.session.commit()
    return jsonify({})
