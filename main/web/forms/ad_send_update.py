from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SendUpdateForm(FlaskForm):
    chat_id = StringField('ID чата', validators=[DataRequired()])
    submit = SubmitField('Отправить')
