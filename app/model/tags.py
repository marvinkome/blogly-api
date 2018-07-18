from flask import jsonify
from .. import db


class Tags(db.Model):
    __tablename__ = 'tags'

    # pylint: disable=no-member

    uuid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    posts = db.relationship('Post', backref='tag', lazy='dynamic')

    @staticmethod
    def create_init_tags():
        initial_tags = ['tech', 'science', 'culture', 'art', 'media']

        for tag in initial_tags:
            t = Tags(name=tag)
            db.session.add(t)

        db.session.commit()

    def __repr__(self):
        return '<Tag %r>' % self.name