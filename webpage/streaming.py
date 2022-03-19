from flask import (
    Response, Blueprint, render_template)
from flask_login import login_required, current_user
from initialization import deny_basic
from initialization import procDict as procD
from initialization import procLock as procL
import os
import cv2

streaming = Blueprint('streaming', __name__)

def streamVideo(d, lock, id):
    while True:
        try:
            with lock:
                _, buffer = cv2.imencode('.jpg', d[id])
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(e)

@streaming.route('/watch-stream')
@deny_basic
@login_required
def watch_stream():
    global dataset
    #dataset = setupDataLoader(source = '0')
    return render_template("watchvideo.html", user=current_user)

@streaming.route('/video-feed1')
@deny_basic
@login_required
def video_feed1():
    os.environ['processingImage'] = 'running'
    return Response(
        streamVideo(procD, procL, 0),
        mimetype='multipart/x-mixed-replace; boundary=frame')