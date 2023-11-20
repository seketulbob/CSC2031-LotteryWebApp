from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    firstname = StringField()
    lastname = StringField()
    phone = StringField()
    password = PasswordField()
    confirm_password = PasswordField()
    submit = SubmitField()
