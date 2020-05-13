from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    ValidationError,
    EqualTo,
    Length,
)

from .registry import registry


def email_available(form, field):
    if not registry.email_available(field.data):
        raise ValidationError('E-mail already in use')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    company = StringField('Company name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email(), email_available])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        EqualTo('confirm', message='Passwords must match'),
        Length(min=8),
    ])
    confirm = PasswordField('Repeat password')
    remember = BooleanField('Remember', default=True)
    agree = BooleanField('', default=False, validators=[DataRequired(), ])
    submit = SubmitField('Create user')


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('remember', default=True)
    submit = SubmitField('Sign In')


class ConsentForm(FlaskForm):
    remember = BooleanField('Remember', default=True)
    grant = SubmitField('Allow')
    deny = SubmitField('Cancel')


# -- Reset/change password flow ----------------------------------------------


class ResetPasswordForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Send verification code via e-mail')


class EnterVerificationCodeForm(FlaskForm):
    verification_code = StringField('Verification code', validators=[DataRequired()])
    submit = SubmitField('Next')


class ChangePasswordForm(FlaskForm):
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Password (confirm)', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Save new password')


# -- Edit profile flow -------------------------------------------------------


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    company = StringField('Company name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Save')
