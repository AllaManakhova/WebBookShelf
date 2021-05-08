from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators
from wtforms import BooleanField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired


class BookForm(FlaskForm):
    # Форма для добавления или изменения конкретной книги.
    # Данные для выбора коллекции заполняются непосредственно при создании формы.
    title = StringField('Название книги', validators=[DataRequired()])
    author = StringField('Автор книги')
    year = IntegerField('Год издания')
    opinion = TextAreaField("Отзыв")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')
    collection_id = RadioField('Коллекция', validators=[validators.Optional()], validate_choice=False)
