from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class AboutMeForm(FlaskForm):
    # Форма для редактирования информации о пользователе.
    # image_path - элемент формы для выбора аватарки пользователя. Сама картинка передается напрямую в html.
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    image_path = FileField("Аватарка")
    submit = SubmitField('Подтвердить изменения')
