from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[Email('Некорректный email')])
    psw = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=4, max=20, message='Пароль должен быть от 4 до 20 символов')])
    remember = BooleanField('Запомнить: ', default=False)
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Имя: ', validators=[Length(min=4, max=20, message='Имя должен быть от 4 до 20 символов')])
    email = StringField('Email: ', validators=[Email('Некорректный email')])
    psw = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=4, max=20,
                                   message='Пароль должен быть от 4 до 20 символов')])
    psw2 = PasswordField('Повтор пароля: ', validators=[DataRequired(), EqualTo('psw', message='Пароли должны совпвдвть')])
    submit = SubmitField('Регистрация')


class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий: ', validators=[Length(min=4, max=20, message='Комментарий должен быть от 4 до 20 символов')])
    submit = SubmitField('Комментировать')


class MessageForm(FlaskForm):
    text = TextAreaField('Сообщение: ', validators=[Length(min=20, max=100, message='Комментарий должен быть от 20 до 100 символов')])
    submit = SubmitField('Отправить')
