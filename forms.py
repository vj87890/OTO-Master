from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20), ])
    DOB= StringField('DOB ', validators=[DataRequired()])
    fathersname = StringField("Father's name",
                           validators=[DataRequired(), Length(min=2, max=20), ])
    address = StringField("Address",
                              validators=[DataRequired(), Length(min=2, max=20), ])
    mobile = IntegerField("Mobile",validators=[DataRequired()])

    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    intro_id=StringField('Introducer Id', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')