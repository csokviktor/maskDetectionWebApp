from flask import (Response, Blueprint,
                    render_template, request,
                    flash, redirect, url_for)
from flask_login import login_required, current_user
from initialization import deny_basic
from detect import processImage, setupDataLoader
import os

streaming = Blueprint('streaming', __name__)

dataset = None


@streaming.route('/watch-stream')
@deny_basic
@login_required
def watch_stream():
    global dataset
    dataset = setupDataLoader(source = '0')
    return render_template("watchvideo.html", user=current_user)


@streaming.route('/video-feed')
@deny_basic
@login_required
def video_feed():
    global dataset
    os.environ['processingImage'] = 'running'
    return Response(processImage(dataset=dataset), mimetype='multipart/x-mixed-replace; boundary=frame')