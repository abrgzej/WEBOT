from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class SendMessageForm(FlaskForm):
    text = TextAreaField('Текст сообщения', validators=[DataRequired()])
    chat_id = StringField('ID чата', validators=[DataRequired()])
    submit = SubmitField('Отправить')
