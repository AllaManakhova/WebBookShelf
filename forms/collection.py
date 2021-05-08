from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class CollectionForm(FlaskForm):
    # Форма для добавления или редактирования коллекции
    title = StringField('Название коллекции', validators=[DataRequired()])
    submit = SubmitField('Применить')
