from graphene import relay, Mutation, Field
from graphql import GraphQLError
from graphene_sqlalchemy import SQLAlchemyObjectType
from flask_jwt_extended import get_jwt_identity

from .. import db
from ..model import Notification as NotificationModel, User as UserModel
from .user import User


class Notification(SQLAlchemyObjectType):
    class Meta:
        model = NotificationModel
        interfaces = (relay.Node, )


class ReadNotifications(Mutation):
    user = Field(lambda: User)

    def mutate(self, info):
        # pylint: disable=no-member
        email = get_jwt_identity()
        if email is None:
            return GraphQLError(
                'You need an access token to perform this action')

        user = UserModel.query.filter_by(email=email).first()

        # get all notifications
        notifications = user.notifications.filter_by(read=False).all()

        for notification in notifications:
            notification.read = True
            db.session.add(notification)

        db.session.commit()

        return ReadNotifications(user=user)
