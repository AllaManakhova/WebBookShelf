import os
from os import abort

from flask import Flask, render_template, request, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from werkzeug.utils import redirect, secure_filename

import books_api
from data import db_session
from data.users import User
from data.books import Book
from data.collections import Collection
from forms.login_form import LoginForm
from forms.book import BookForm
from forms.about_me import AboutMeForm
from forms.collection import CollectionForm
from forms.user import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(books_api.blueprint)

    @app.route("/")
    def index():
        # Стандартное перенаправление, если пользователь зашел в корень
        return redirect('/books')

    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        # Метод для создания нового пользователя
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User()
            user.name = form.name.data
            user.email = form.email.data
            user.about = form.about.data
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Метод для авторизации пользователя в систему
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        # Метод для выхода пользователя
        logout_user()
        return redirect("/")

    @app.route('/unauthorized_user')
    def unauthorized_user():
        # Метод, отображающий шаблон, если пользователь не авторизован
        return render_template('unauthorized_user.html', title='Вы не авторизированы!')

    @app.route('/about_me', methods=['GET', 'POST'])
    def about_me():
        # Метод для просмотра или изменения информации о пользователе.
        # Позволяет загружать аватарку пользователя, если он ее выбрал и она отличается от его текущей
        form = AboutMeForm()

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if request.method == "GET":
            if user:
                form.name.data = user.name
                form.about.data = user.about
            else:
                abort(404)

        if request.method == "POST" and form.validate_on_submit():
            user.about = form.about.data
            user.name = form.name.data
            if form.image_path.data:
                filename = secure_filename(form.image_path.data.filename)
                if user.image_path != filename:
                    file = open('static/img/' + filename, 'w+')
                    file.close()
                    form.image_path.data.save('static/img/' + filename)
                    user.image_path = filename
            db_sess.commit()

        return render_template('about_me.html', title='О себе', form=form, avatar=user.image_path)

    @app.route('/books', methods=['GET'])
    def books_view():
        # Метод для просмотра книг, принадлежащих пользователю или публичных книг
        db_sess = db_session.create_session()
        if current_user.is_authenticated:
            books = db_sess.query(Book).filter((Book.user == current_user) | (Book.is_private is not True))
        else:
            books = db_sess.query(Book).filter(Book.is_private != True)
        return render_template("index.html", books=books)

    @app.route('/collections', methods=['GET'])
    def collections_view():
        # Метод для просмотра списка коллекций, принадлежащих пользователю
        db_sess = db_session.create_session()
        if current_user.is_authenticated:
            collections = db_sess.query(Collection).filter((Collection.user == current_user))
            return render_template("index.html", collections=collections)
        else:
            return redirect('/unauthorized_user')

    @app.route('/book', methods=['GET', 'POST'])
    @login_required
    def add_book():
        # Метод для добавления новой книги.
        # Информация о коллекция выбирается автоматически из коллекций, принадлежащих пользователю.
        # Из-за того, что в RadioField находится только индекс выбранного элемента, выбор коллекции производится вручную
        form = BookForm()

        db_sess = db_session.create_session()
        if current_user.is_authenticated:
            collections = db_sess.query(Collection).filter((Collection.user == current_user))
        else:
            collections = []

        index = form.collection_id.data

        if request.method == "POST" and form.validate_on_submit():
            db_sess = db_session.create_session()
            book = Book()
            book.title = form.title.data
            book.author = form.author.data
            book.opinion = form.opinion.data
            book.year = form.year.data
            book.is_private = form.is_private.data
            if index is not None:
                book.collection_id = collections[int(index) - 1].id
            current_user.books.append(book)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/books')

        choices = []
        for item in collections:
            choices.append((item.id, item.name))
        form.collection_id.choices = choices

        return render_template('add_book.html', title='Добавление книги', form=form, collections=collections.count())

    @app.route('/book/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_books(id):
        # Метод для редактирования книги.
        # Информация о коллекция выбирается автоматически из коллекций, принадлежащих пользователю.
        # Из-за того, что в RadioField находится только индекс выбранного элемента, выбор коллекции производится вручную
        db_sess = db_session.create_session()
        if current_user.is_authenticated:
            collections = db_sess.query(Collection).filter((Collection.user == current_user))
        else:
            collections = []
        form = BookForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            book = db_sess.query(Book).filter(Book.id == id,
                                              Book.user == current_user).first()
            choices = []
            for item in collections:
                choices.append((item.id, item.name))
            form.collection_id.choices = choices

            if book:
                form.title.data = book.title
                form.author.data = book.author
                form.opinion.data = book.opinion
                form.year.data = book.year
                if book.collection_id is not None:
                    index = 0
                    for col in collections:
                        index += 1
                        if col.id == book.collection_id:
                            form.collection_id.data = str(index)
                form.is_private.data = book.is_private
            else:
                abort(404)
        if request.method == "POST" and form.validate_on_submit():
            db_sess = db_session.create_session()
            book = db_sess.query(Book).filter(Book.id == id,
                                              Book.user == current_user).first()
            index = form.collection_id.data
            if book:
                book.title = form.title.data
                book.author = form.author.data
                book.opinion = form.opinion.data
                book.year = form.year.data
                book.is_private = form.is_private.data
                if index is not None:
                    book.collection_id = collections[int(index) - 1].id
                db_sess.commit()
                return redirect('/books')
            else:
                abort(404)
        return render_template('edit_book.html', title='Редактирование книги', form=form,
                               collections=collections.count())

    @app.route('/book_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def book_delete(id):
        # Метод для удаления книги, если она имеется и ее создавал пользователь
        db_sess = db_session.create_session()
        book = db_sess.query(Book).filter(Book.id == id,
                                          Book.user == current_user).first()
        if book:
            db_sess.delete(book)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/')

    @app.route('/collection', methods=['GET', 'POST'])
    @login_required
    def add_collection():
        # Метод для создания новой коллекции, которая автоматически привязывается к пользователю
        form = CollectionForm()
        if request.method == "POST" and form.validate_on_submit():
            db_sess = db_session.create_session()
            collection = Collection()
            collection.name = form.title.data
            current_user.collections.append(collection)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/collections')
        return render_template('add_collection.html', title='Добавление коллекции',
                               form=form)

    @app.route('/collection/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_collection(id):
        # Метод для редактирования информации о коллекции
        form = CollectionForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            collection = db_sess.query(Collection).filter(Collection.id == id,
                                                          Collection.user == current_user).first()
            if collection:
                form.title.data = collection.name
            else:
                abort(404)
        if request.method == "POST" and form.validate_on_submit():
            db_sess = db_session.create_session()
            collection = db_sess.query(Collection).filter(Collection.id == id,
                                                          Collection.user == current_user).first()
            if collection:
                collection.name = form.title.data
                db_sess.commit()
                return redirect('/collections')
            else:
                abort(404)
        return render_template('edit_collection.html',
                               title='Редактирование коллекции',
                               form=form)

    @app.route('/view_collection/<int:id>', methods=['GET'])
    @login_required
    def view_collection(id):
        # Метод для просмотра списка книг в коллекции пользователя
        db_sess = db_session.create_session()
        collection = db_sess.query(Collection).filter(Collection.id == id,
                                                      Collection.user == current_user).first()
        if collection:
            return render_template('view_collection.html', collection=collection)
        else:
            abort(404)

    @app.route('/book_remove_from_collection/<int:id>/<int:collection_id>', methods=['GET', 'POST'])
    @login_required
    def book_remove_from_collection(id, collection_id):
        # Метод для удаления книги из коллекции, если они связаны.
        # collection_id используется для перехода на страницу просмотра коллекции
        db_sess = db_session.create_session()
        book = db_sess.query(Book).filter(Book.id == id,
                                          Book.user == current_user).first()
        if book:
            book.collection_id = None
            db_sess.commit()
            return redirect('/view_collection/' + str(collection_id))
        else:
            abort(404)

    @app.route('/collection_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def collection_delete(id):
        # Метод для удаления коллекции, если пользователь ее создавал и она присутствует
        db_sess = db_session.create_session()
        collection = db_sess.query(Collection).filter(Collection.id == id,
                                                      Collection.user == current_user).first()
        if collection:
            db_sess.delete(collection)
            db_sess.commit()
        else:
            abort(404)
        return redirect('/collections')

    @app.errorhandler(404)
    def not_found(_):
        # Обработка некрректного запроса
        return make_response(jsonify({'error': 'Not found'}), 404)

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
