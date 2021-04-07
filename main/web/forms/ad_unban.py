from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class UnbanForm(FlaskForm):
    block_id = StringField('ID пользователя для разблокировки', validators=[DataRequired()])
    submit = SubmitField('Разблокировать')
