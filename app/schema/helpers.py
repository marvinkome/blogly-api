import graphene
from sqlalchemy import desc
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphene_sqlalchemy.utils import get_query


class CountableConnection(graphene.relay.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    @staticmethod
    def resolve_total_count(root, info, *args, **kwargs):
        return root.length


class CustomSQLAlchemyObjectType(SQLAlchemyObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls,
                                    model=None,
                                    registry=None,
                                    skip_registry=False,
                                    only_fields=(),
                                    exclude_fields=(),
                                    connection=None,
                                    connection_class=None,
                                    use_connection=None,
                                    interfaces=(),
                                    id=None,
                                    _meta=None,
                                    **options):
        # Force it to use the countable connection
        countable_conn = connection or CountableConnection.create_type(
            "{}CountableConnection".format(model.__name__), node=cls)

        super(CustomSQLAlchemyObjectType, cls).__init_subclass_with_meta__(
            model,
            _meta=_meta,
            interfaces=interfaces,
            connection=countable_conn,
            **options)


class DescSortAbleConnectionField(SQLAlchemyConnectionField):
    @classmethod
    def get_query(cls, model, info, sort_by=None, **args):
        return get_query(model, info.context).order_by(desc(sort_by))
