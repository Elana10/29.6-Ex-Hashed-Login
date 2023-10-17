from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, ValidationError
from sqlalchemy import select
from models import User

def my_length_check(max = 0):
    message = f"Must be no more than {max} characters long."

    def _length(form, field):
        l = field.data and len(field.data) or 0
        if l > max:
            raise ValidationError(message)
    
    return _length 

def unique_username():
    message = "Username already exists. Please choose a unique username."

    def _unique(form, field):
        u = field.data
        if User.query.filter_by(username=u).first():
            raise ValidationError(message)
    return _unique

def unique_email():
    message = "Email is already associated to another user. Please use a different email address."

    def _unique(form, field):
        e = field.data
        if User.query.filter_by(email=e).first():
            raise ValidationError(message)
    return _unique

class UserForm(FlaskForm):
    username = StringField("Username", validators = [InputRequired(), my_length_check(20), unique_username()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), unique_email()])
    first_name = StringField("First Name", validators=[InputRequired(), my_length_check(30)])
    last_name = StringField("Last Name", validators=[InputRequired(), my_length_check(30)])

class Login(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class Comment(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), my_length_check(100)])
    content = StringField("Content", validators=[InputRequired()])