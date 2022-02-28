from flask import (Response, Blueprint,
                    render_template, request)
from flask_login import login_required, current_user
from initialization import deny_basic, db
from modeldec import Cameras

camerahandling = Blueprint('camerahandling', __name__)

@camerahandling.route('/camera-management', methods=['GET', 'POST'])
@login_required
@deny_basic
def camera_management():
    cameras = Cameras.query.all()
    return render_template('cameramanagement.html', cameras=cameras)