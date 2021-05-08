import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase, SerializerMixin):
    # Модель книги, которая имеет ссылку на пользователя, который ее создал, а также на коллекцию, в которую
    # она входит
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    opinion = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    collection_id = sqlalchemy.Column(sqlalchemy.Integer,
                                      sqlalchemy.ForeignKey("collections.id"),
                                      nullable=True)

    user = orm.relation("User")
    collection = orm.relation("Collection")

    def __repr__(self):
        return f'<Book> {self.id} {self.name} {self.author} {self.year}'
