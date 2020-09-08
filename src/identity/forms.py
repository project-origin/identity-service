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


class LengthIf(Length):
    """
    A 'Length' validator which only performs validation if any of
    the [other] form fields has a truthy value, ie. length is optional
    if none of the fields has a value.
    """
    def __init__(self, other_field_names, *args, **kwargs):
        self.other_field_names = other_field_names
        super(LengthIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        for other_field_name in self.other_field_names:
            other_field = form._fields.get(other_field_name)

            if other_field is None:
                raise RuntimeError('No field named "%s" in form' % other_field_name)

            if bool(other_field.data):
                super(LengthIf, self).__call__(form, field)


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    company = StringField('Company name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    current_password = PasswordField('Current password', validators=[LengthIf(['current_password', 'password1', 'password2'], min=8)])
    password1 = PasswordField('New password', validators=[LengthIf(['current_password', 'password1', 'password2'], min=8)])
    password2 = PasswordField('New password (confirm)', validators=[LengthIf(['current_password', 'password1', 'password2'], min=8)])
    submit = SubmitField('Save profile')


# -- Create/delete OAUTH2 clients flow ---------------------------------------


class CreateOauth2ClientForm(FlaskForm):
    id = StringField('Client ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    secret = StringField('Secret', validators=[DataRequired()])
    callback = StringField('Callback URL', validators=[DataRequired()])
    submit = SubmitField('Create client')
