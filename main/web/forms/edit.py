from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired

from main.constants.web import SUBJECT_LIST


class EditForm(FlaskForm):
    subject = SelectField('Предмет', validators=[DataRequired()], choices=SUBJECT_LIST)
    text = StringField('Новое д/з', validators=[DataRequired()])
    submit = SubmitField('Изменить')
