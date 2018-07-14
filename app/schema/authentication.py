import graphene
import re
from graphql import GraphQLError
from flask_jwt_extended import (create_refresh_token,
                                jwt_refresh_token_required,
                                create_access_token, get_jwt_identity)
from ..model import User as UserModel
from .. import db


def validate_password(password):
    regExp = re.compile('^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|\
                        ((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})')
    r = regExp.match(password)
    if r is not None:
        return True
    else:
        return False


class LoginUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()

    def mutate(self, info, email, password):
        # check if user already exists
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            return GraphQLError('No user found with this email')

        # check if password is correct
        check_password = user.verify_password(password)
        if not check_password:
            return GraphQLError('Password doesn\'t match with this email')

        refresh_token = create_refresh_token(identity=user.username)

        return LoginUser(token=refresh_token)


class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        full_name = graphene.String(required=True)

    token = graphene.String()

    def mutate(self, info, email, username, password, full_name):
        # pylint: disable=no-member

        # check if password is valid
        if validate_password(password) is False:
            return GraphQLError('Invalid password')

        # check if email is available
        if UserModel.query.filter_by(email=email).first():
            return GraphQLError('Email is already taken')

        # check if username is available
        if UserModel.query.filter_by(username=username).first():
            return GraphQLError('Username is already taken')

        user = UserModel(
            email=email,
            username=username,
            full_name=full_name,
            password=password)
        db.session.add(user)
        db.session.commit()

        refresh_token = create_refresh_token(identity=user.username)

        return CreateUser(token=refresh_token)


class RefreshToken(graphene.Mutation):
    token = graphene.String()

    @jwt_refresh_token_required
    def mutate(self, info):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return RefreshToken(token=access_token)