from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, ValidationError
from wtforms import StringField, PasswordField, BooleanField, SubmitField

from .registry import registry


def email_available(form, field):
    if not registry.email_available(field.data):
        raise ValidationError('E-mail already in use')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    company = StringField('Company name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email(), email_available])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember')
    submit = SubmitField('Create user')


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('remember')
    submit = SubmitField('Sign In')


class ConsentForm(FlaskForm):
    remember = BooleanField('Remember')
    grant = SubmitField('Allow')
    deny = SubmitField('Cancel')
