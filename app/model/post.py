from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import desc, and_
from flask_sqlalchemy import SessionBase
from datetime import datetime
from .. import db
from ..helpers import generate_graphql_token

from .tags import Tags
from .user import User


class Post(db.Model):
    __tablename__ = 'posts'

    # pylint: disable=no-member
    uuid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_pic_url = db.Column(db.String(256))
    views = db.Column(db.Integer, default=0)

    author_id = db.Column(db.Integer, db.ForeignKey('users.uuid'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.uuid'))

    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    claps = db.relationship('Clap', backref='post', lazy='dynamic')
    notification = db.relationship(
        'Notification', backref='post', lazy='dynamic')

    @hybrid_property
    def next_title(self):
        query = SessionBase.object_session(self).query(Post)

        post_filter = query.filter(
            and_(Post.timestamp > self.timestamp, Post.uuid != self.uuid))

        res = post_filter.order_by(Post.timestamp).first()
        return res.title if res is not None else res

    @hybrid_property
    def prev_title(self):
        query = SessionBase.object_session(self).query(Post)

        post_filter = query.filter(
            and_(Post.timestamp < self.timestamp, Post.uuid != self.uuid))

        res = post_filter.order_by(Post.timestamp.desc()).first()

        return res.title if res is not None else res

    @staticmethod
    def generate_fake(count=10):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        tag_count = Tags.query.count()

        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            t = Tags.query.offset(randint(0, tag_count - 1)).first()
            p = Post(
                title=forgery_py.lorem_ipsum.title(3),
                body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                timestamp=forgery_py.date.date(True),
                post_pic_url=None,
                author=u,
                tag=t)

            db.session.add(p)

        db.session.commit()

    def __repr__(self):
        return '<Post %r>' % self.title
