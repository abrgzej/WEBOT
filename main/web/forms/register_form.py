from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    password1 = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Пароль ещё раз', validators=[DataRequired()])
    position = RadioField('Должность', validators=[DataRequired()], choices=['Администратор', 'Редактор'], )
    submit = SubmitField('Зарегистрироваться')
