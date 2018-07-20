import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphql import GraphQLError

from flask_jwt_extended import get_jwt_identity

from sqlalchemy import func

from ..model import User as UserModel, Post as PostModel
from .user import User, UpdateProfilePic, UpdateInfo
from .post import Post, CreatePost, UpdatePost, DeletePost, ViewPost
from .comment import Comment, CreateComment, CreateReplyComment
from .claps import Clap, CreateClap
from .tags import Tags, CreateTag
from .notifications import Notification
from .authentication import LoginUser, CreateUser, RefreshToken
from .helpers import DescSortAbleConnectionField


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    view_post = ViewPost.Field()

    create_tag = CreateTag.Field()

    update_user_profile_pic = UpdateProfilePic.Field()
    update_user_info = UpdateInfo.Field()

    create_comment = CreateComment.Field()
    create_comment_reply = CreateReplyComment().Field()

    create_clap = CreateClap.Field()

    login_user = LoginUser.Field()
    create_user = CreateUser.Field()
    refresh_token = RefreshToken.Field()


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    # all posts
    all_post = DescSortAbleConnectionField(
        Post, sort_by=graphene.Argument(graphene.String))

    post = graphene.Field(Post, title=graphene.String())
    user = graphene.Field(User)

    notifications = graphene.List(
        Notification, email=graphene.String(), sort=graphene.Boolean())

    public_user = graphene.Field(User, name=graphene.String())

    def resolve_post(self, info, title):
        query = Post.get_query(info)
        res = query.filter(func.lower(PostModel.title) == title).first()
        return res

    def resolve_user(self, info):
        query = User.get_query(info)
        email = get_jwt_identity()
        if email is None:
            return GraphQLError('You need an Access token to get this data')

        res = query.filter_by(email=email).first()
        if res is None:
            return GraphQLError('Token is invalid')

        return res

    def resolve_public_user(self, info, name):
        query = User.get_query(info)
        res = query.filter(func.lower(UserModel.full_name) == name).first()
        return res

    def resolve_notifications(self, info, email, sort=False):
        query = Notification.get_query(info)
        user = UserModel.query.filter_by(email=email).first()
        if user is None:
            return GraphQLError('Email is invalid')

        if sort is False:
            return query.filter_by(author=user)

        return query.filter_by(author=user, read=False)


schema = graphene.Schema(query=Query, mutation=Mutation)
