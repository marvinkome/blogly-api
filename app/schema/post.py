import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import GraphQLError
from flask_jwt_extended import get_jwt_identity

from ..model import Post as PostModel, User as UserModel
from .. import db
from .helpers import CustomSQLAlchemyObjectType


class Post(CustomSQLAlchemyObjectType):
    # pylint: disable=no-member
    class Meta:
        model = PostModel
        interfaces = (relay.Node, )

    def resolve_next_title(self, _):
        return self.next_title

    def resolve_prev_title(self, _):
        return self.prev_title


class PostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    body = graphene.String(required=True)
    post_pic_url = graphene.String()


class ViewPost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)

    post = graphene.Field(lambda: Post)

    def mutate(self, info, post_id):
        post = PostModel.query.filter_by(uuid=post_id).first()
        if post is not None:
            views = post.views
            if views is not None:
                post.views += 1
            else:
                post.views = 1

        # pylint: disable=no-member
        db.session.add(post)
        db.session.commit()
        return ViewPost(post=post)


class CreatePost(graphene.Mutation):
    class Arguments:
        post_data = PostInput(required=True)

    post = graphene.Field(lambda: Post)

    def mutate(self, info, post_data=None):
        email = get_jwt_identity()
        if email is None:
            return GraphQLError(
                'You need an access token to perform this action')

        user = UserModel.query.filter_by(email=email).first()

        if post_data.post_pic_url is not None:
            post = PostModel(
                title=post_data.title,
                body=post_data.body,
                post_pic_url=post_data.post_pic_url)
        else:
            post = PostModel(title=post_data.title, body=post_data.body)

        post.author = user

        # pylint: disable=no-member
        db.session.add(post)
        db.session.commit()
        return CreatePost(post=post)


class UpdatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        body = graphene.String()
        post_pic_url = graphene.String()
        post_id = graphene.Int(required=True)

    post = graphene.Field(lambda: Post)

    def mutate(self, info, post_id, title=None, body=None, post_pic_url=None):
        email = get_jwt_identity()
        if email is None:
            return GraphQLError(
                'You need an access token to perform this action')

        post = PostModel.query.filter_by(uuid=post_id).first()
        if post is not None:
            if title is not None:
                post.title = title
            if body is not None:
                post.body = body
            if post_pic_url is not None:
                post.post_pic_url = post_pic_url

        # pylint: disable=no-member
        db.session.add(post)
        db.session.commit()
        return UpdatePost(post=post)


class DeletePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)

    post = graphene.Field(lambda: Post)

    def mutate(self, info, post_id):
        email = get_jwt_identity()
        if email is None:
            return GraphQLError(
                'You need an access token to perform this action')

        post = PostModel.query.filter_by(uuid=post_id).first()
        if post is not None:
            # pylint: disable=no-member
            db.session.delete(post)
            db.session.commit()

        return DeletePost(post=post)