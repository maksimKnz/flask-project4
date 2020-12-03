import phonenumbers
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError


def check_phone(form, field):
    number = form.phone.data
    try:
        if not phonenumbers.is_valid_number(phonenumbers.parse(number, 'RU')):
            raise phonenumbers.NumberParseException(None, None)
    except phonenumbers.NumberParseException:
        raise ValidationError('Пожалуйста укажите номер телефона полностью (+7ХХХХХХХХХХ)')


def mail_check(form, field):
    msg = "Пожалуйста укажите корректный адрес электронной почты"
    mail = field.data
    if mail.find('@') == -1 or len(field.data) < 5:
        raise ValidationError(msg)


class LoginForm(FlaskForm):
    mail = StringField("Электропочта:", validators=[mail_check])
    password = PasswordField("Пароль:")


class RegistrationForm(FlaskForm):
    mail = StringField("Электропочта:", validators=[mail_check])
    password = PasswordField("Пароль:", validators=[DataRequired(), Length(min=5, message="Пароль должен быть не менее 5 символов")])


class OrderForm(FlaskForm):
    order_cart = HiddenField()
    order_summ = HiddenField()
    name = StringField('Ваше имя', validators=[Length(min=2, message='Пожалуйста укажите ваше имя')])
    address = StringField('Адрес ')
    mail = StringField('Электропочта:', validators=[mail_check])
    phone = StringField('Телефон', validators=[check_phone])
