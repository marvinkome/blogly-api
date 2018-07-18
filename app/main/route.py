import re
import os

from flask import make_response, request, jsonify, url_for, send_from_directory, current_app as app
from flask_graphql import GraphQLView
from flask_sqlalchemy import get_debug_queries

from flask_jwt_extended import (jwt_required, jwt_optional,
                                create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_refresh_token_required)

from . import main
from .. import db, jwt
from ..model import User
from ..schema import schema


def graphql():
    graphqli = os.environ.get('USE_GRAPHQLI') or False
    g = GraphQLView.as_view(
        'graphql',
        schema=schema,
        context={'session': db.session},
        graphiql=graphqli,
    )

    return jwt_optional(g)


main.add_url_rule('/graphql', view_func=graphql())

@main.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token})


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= app.config['FLASKY_DB_QUERY_TIMEOUT']:
            app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response
