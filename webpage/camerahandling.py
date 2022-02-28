from flask import (Response, Blueprint,
                    render_template, request)
from flask_login import login_required, current_user
from initialization import deny_basic, db
from modeldec import Cameras

camerahandling = Blueprint('camerahandling', __name__)