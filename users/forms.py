from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
import re

def character_check(form, field):

    excluded_chars = "*?!'^+%&/()=}][{$#@<>"  # Input filtering the special character

    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed.")

def validate_phone(self, data_field):
    p = re.compile("[0-9]{4}[-][0-9]{3}[-][0-9]{4}")  # Regex for phone number validation
    if not p.match(data_field.data):
        raise ValidationError(f"Phone number must contain digits in the form 'XXXX-XXX-XXXX'")

def validate_password(self, password):

    p = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=!])(?=\S+$).{6,12}$') # Regex for password validation

    if not p.match(password.data):
        raise ValidationError(f"Password must be between 6 and 12 characters and contain at least 1 digit, 1 lowercase "
                              f"and 1 uppercase word character, and 1 special character.")
class RegisterForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    firstname = StringField(validators=[DataRequired(), character_check])
    lastname = StringField(validators=[DataRequired(), character_check])
    phone = StringField(validators=[DataRequired(), validate_phone])
    password = PasswordField(validators=[DataRequired(), validate_password])
    confirm_password = PasswordField(validators=[EqualTo('password', message='Password must match'), DataRequired()])
    submit = SubmitField()
