from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class JournalForm(FlaskForm):
    id = StringField('JournalID', validators=[DataRequired()])
    today = DateField('Today', format='%Y-%m-%d', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    future = StringField('Future', validators=[DataRequired()])
    comment = StringField('Comment')
    account_id = IntegerField('AccountID', validators=[DataRequired()])
    startDate = DateField('StartDate', validators=[DataRequired()])
    endDate = DateField('EndDate', validators=[DataRequired()])
