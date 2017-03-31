from wtforms import Form, TextField, SelectField, BooleanField, StringField, PasswordField, validators, TextAreaField, IntegerField, HiddenField, RadioField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Length, InputRequired, EqualTo, Email
from datetime import datetime
from pyconf import *
from werkzeug.utils import secure_filename


thisyear=datetime.now().year
years=[(x,x) for x in range((thisyear + 5), (pyalumni_first -1), -1)]

class UserLoginForm(Form):
    email = TextField('Email address', [InputRequired(message='You need to specify an Email address.')]) #, [InputRequired(), Email()])
    password = PasswordField('Password')#, [validators.Required(), validators.Length(min=6, max=200)])

class UserRegisterForm(Form):
    email = TextField('Email', [InputRequired(message='You have to specify an Email address.'), Email(message='This needs to be a valid Email address.')])
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    class_year = SelectField('Year', choices=years, coerce=int, validators=[validators.optional()])

class UserPasswordForm(Form):
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class UserEditForm(Form):
    email = TextField('Email', [InputRequired(message='You have to specify an Email address.'), Email(message='This needs to be a valid Email address.')])
    #password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    #confirm = PasswordField('Repeat Password')
    admin = BooleanField('Is this user an admin')
    authenticated = BooleanField('Has user authenticated?')
    class_year = SelectField('Year', choices=years, coerce=int, validators=[validators.optional()])

class PickStudentForm(Form):
    students = SelectField('Select existing record', coerce=int, validators=[validators.optional()])

class StudentEditForm(Form):
    firstname = TextField('First name', [InputRequired(message='Please enter your first name.')])
    lastname = TextField('Last name', [InputRequired(message='Please enter your last name.')])
    spouse = TextField('Your spouse', validators=[validators.optional()])
    birthday = TextField('Birthday (year and month only please)', validators=[validators.optional()])
    site = TextField('Your blog/website', validators=[validators.optional()])
    employer = TextField('Name of your company', validators=[validators.optional()])
    kids = TextField('Name of your kids', validators=[validators.optional()])
    location = TextAreaField('location', validators=[validators.optional()])
    email = TextField('email', validators=[validators.optional()])
    obit = TextAreaField('Deceased? Please leave any details you would like to share.', validators=[validators.optional()])
    bio = TextAreaField('Tell us about yourself.', validators=[validators.optional()])
    class_year = SelectField('Year', choices=years, coerce=int)

class StudentChangeImage(Form):
    image = RadioField('Profile Image', coerce=str)
    setphoto = SubmitField(label='Select Photo')
    deletephoto = SubmitField(label='Delete Photo')
