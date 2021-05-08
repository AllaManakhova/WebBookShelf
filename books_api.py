import flask
from flask import jsonify, request

from data import db_session
from data.books import Book

blueprint = flask.Blueprint(
    'books_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/books', methods=['GET'])
def get_books():
    # Апи получения всех книг
    db_sess = db_session.create_session()
    books = db_sess.query(Book).all()
    return jsonify(
        {
            'books':
                [item.to_dict(only=('title', 'author', 'year', 'user.name'))
                 for item in books]
        }
    )


@blueprint.route('/api/books/<int:book_id>', methods=['GET'])
def get_one_news(book_id):
    # Апи получения книги по ее id.
    # Если книгу не удалось найти, вернется ошибка
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    if not book:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'book': book.to_dict(only=('title', 'author', 'year', 'user.name', 'is_private'))
        }
    )


@blueprint.route('/api/books', methods=['POST'])
def create_book():
    # Апи для добавления книги.
    # Если какой-то из параметров не передан, то будет возвращена ошибка
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'author', 'year', 'is_private', 'user_id']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    book = Book()
    book.title = request.json['title']
    book.author = request.json['author']
    book.year = request.json['year']
    book.is_private = request.json['is_private']
    book.user_id = request.json['user_id']
    db_sess.add(book)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_news(book_id):
    # Апи удаления книги по ее id.
    # Если книгу не удалось найти, вернется ошибка
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    if not book:
        return jsonify({'error': 'Not found'})
    db_sess.delete(book)
    db_sess.commit()
    return jsonify({'success': 'OK'})
