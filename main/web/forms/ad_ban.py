from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class BanForm(FlaskForm):
    block_id = StringField('ID пользователя для блокировки', validators=[DataRequired()])
    submit = SubmitField('Заблокировать')
