from flask import Blueprint, redirect, render_template, request, jsonify, flash, url_for
from flask_login import login_required, current_user
from initialization import deny_basic, db
import initialization
from modeldec import Cameras
from parallelDetect import runSubscriber
import json
import threading

camerahandling = Blueprint('camerahandling', __name__)

def add_live_camera(id, ip, port):
    host = f"{ip}:{port}"
    t = threading.Thread(
        target=runSubscriber,
        args=(host, id, initialization.inpDict, initialization.inpLock))
    t.start()
    initialization.tasks[id] = t

def stop_live_camera(id):
    pass

@camerahandling.route('/camera-management', methods=['GET', 'POST'])
@login_required
@deny_basic
def camera_management():
    # handle adding new camera to db
    if request.method == 'POST':
        ip = request.form.get('host')
        port = request.form.get('port')
        camera = Cameras.query.filter_by(ip=ip, port=port).first()
        if camera:
            flash('Camera already exists with given Host', category='error')
        else:
            new_camera = Cameras(
                ip=ip,
                port=port
            )
            db.session.add(new_camera)
            db.session.commit()
            commited_camera = Cameras.query.filter_by(ip=ip, port=port).first()
            add_live_camera(commited_camera.id, commited_camera.ip, commited_camera.port)
            flash('New Camera added', category='success')
            return redirect(url_for('camerahandling.camera_management'))

    cameras = Cameras.query.all()
    return render_template(
        'cameramanagement.html', user=current_user,
        cameras=cameras)

@camerahandling.route('/delete-camera', methods=['POST'])
@deny_basic
def delete_user():
    data = json.loads(request.data)
    cameraID = data['cameraID']
    camera = Cameras.query.get(cameraID)
    if camera:
        db.session.delete(camera)
        db.session.commit()
        flash('Camera deleted', category='success')
    return jsonify({})