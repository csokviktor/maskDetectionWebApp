from flask import Blueprint, Response, request, jsonify
from sqlalchemy import desc
from initialization import db
from modeldec import Notifications

from datetime import datetime, timedelta
import json

notification = Blueprint('notification', __name__)


@notification.route('/new-notification', methods=['POST'])
def add_new_notification():
    required_fields = [column.key for column in Notifications.__table__.columns][2:]
    try:
        content = json.loads(request.get_json(force=True))
    except Exception as e:
        print(e)
        return Response('JSON is not parsable', status=500)

    res = all(elem in required_fields for elem in content.keys())
    if not res:
        return Response('Not all keys are satisfied', status=500)

    # Get the latest notification from the same camera with same topic
    latest_notification = Notifications.query.filter_by(
        cameraID=content['cameraID'],
        status=content['status']).order_by(desc(Notifications.ts)).first()
    if latest_notification is not None:
        # Drop notification if the same status from the same camera is
        # less then 5s older
        time_diff = (datetime.utcnow()-latest_notification.ts).total_seconds()
        if time_diff < 5.0:
            return Response(status=208)

    new_notification = Notifications(
        ts=datetime.utcnow(),
        cameraID=content['cameraID'],
        status=content['status']
    )
    db.session.add(new_notification)
    db.session.commit()
    return Response(status=200)


@notification.route('/get-notifications', methods=['GET'])
def get_notification():
    notifications = Notifications.query.all()
    temp_dict = {'notifications': []}
    for notification in notifications:
        temp_dict['notifications'].append(jsonify(
            id=notification.id,
            ts=notification.ts,
            cameraID=notification.cameraID,
            status=notification.status
        ).get_json())
    return Response(json.dumps(temp_dict), status=200, content_type='application/json')
