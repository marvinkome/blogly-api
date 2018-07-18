from jwt import DecodeError
from flask_jwt_extended import decode_token, set_access_cookies
from flask import request
from flask_graphql import GraphQLView
from functools import wraps
from operator import itemgetter
from flask_socketio import disconnect, emit
from . import db
from .model import User
import json


def load_user(email):
    return User.query.filter_by(email=email).first()


def verify_token(auth_header):
    if (auth_header is not None):
        token = auth_header.split(' ')[1]
        token = token.strip('"')
        try:
            decoded_token = decode_token(token)
        except DecodeError:
            return False, None

        email = decoded_token['identity']
        user = load_user(email)

        if user is not None:
            return True, user

        return False, None

    return False, None


def auth_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        verified = verify_token(auth_header)
        if verified[0]:
            return fn(verified[1], *args, **kwargs)
        else:
            disconnect()

    return decorator


def save_to_db(data):
    # pylint: disable=no-member
    db.session.add(data)
    db.session.commit()
    return True


def generate_graphql_token(tablename, key):
    import base64
    return base64.b64encode((tablename + ':' + str(key)).encode()).decode()


def get_unread_notifications(user):
    notifications = user.notifications.all()
    unread_notification_count = user.notifications.filter_by(
        read=False).count()
    all_notifications = [
        notification.to_json() for notification in notifications
    ]
    return dict(
        notifications=sorted(
            all_notifications, key=itemgetter('timestamp'), reverse=True)[:10],
        unread_count=unread_notification_count)


def read_all_notifications(user):
    # pylint: disable=no-member
    notifications = user.notifications.filter_by(read=False).all()
    for notification in notifications:
        notification.read = True
        db.session.add(notification)

    db.session.commit()

