import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Collection(SqlAlchemyBase, SerializerMixin):
    # Модель коллекции, которая описывает семейство книг.
    # Имеется ссылка на пользователя, который ее создал, а также на список книг, которые входят в коллекцию
    __tablename__ = 'collections'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    user = orm.relation("User")
    books = orm.relation("Book", back_populates='collection')

    def __repr__(self):
        return f'<Collection> {self.id} {self.name}'
