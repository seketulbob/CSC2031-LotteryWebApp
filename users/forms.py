from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError
import re

def character_check(form, field):

    excluded_chars = "*?!'^+%&/()=}][{$#@<>"

    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed.")

def validate_phone(self, data_field):
    p = re.compile("[0-9]{4}[-][0-9]{3}[-][0-9]{4}")
    if not p.match(data_field.data):
        raise ValidationError(f"Phone number must be in the form 'XXXX-XXX-XXXX'")


class RegisterForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    firstname = StringField(validators=[DataRequired(), character_check])
    lastname = StringField(validators=[DataRequired(), character_check])
    phone = StringField(validators=[DataRequired(), validate_phone])
    password = PasswordField()
    confirm_password = PasswordField()
    submit = SubmitField()
