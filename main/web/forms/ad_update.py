from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class UpdateForm(FlaskForm):
    with open('../all/db/update', 'r', encoding='utf-8') as f:
        re = f.read()
    utext = TextAreaField('Текст обновления', validators=[DataRequired()], default=re)
    submit = SubmitField('Сохранить')
