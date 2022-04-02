from flask import (
    Response, Blueprint, render_template)
from flask_login import login_required, current_user
from modeldec import Cameras
import initialization
import cv2

streaming = Blueprint('streaming', __name__)

def streamVideo(processedDict, lock, id: int):
    while True:
        try:
            with lock:
                _, buffer = cv2.imencode('.jpg', processedDict[id])
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(e)

@streaming.route('/watch-stream')
@initialization.deny_basic
@login_required
def watch_stream():
    cameraIDs = [camera.id for camera in Cameras.query.all()]
    return render_template("watchvideo.html", user=current_user, cameraids=cameraIDs)

@streaming.route('/video-feed/<int:id>')
@initialization.deny_basic
@login_required
def video_feed(id):
    return Response(
        streamVideo(initialization.procDict, initialization.procLock, id),
        mimetype='multipart/x-mixed-replace; boundary=frame')