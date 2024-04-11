from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,TextAreaField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


#------------------------ Class Form ------------------------#
# Create a User Form
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    user_name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField('Favorite Color')
    about_author = TextAreaField('About Author')
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('verify_password_hash', message='Passwords Must Match!') ])
    verify_password_hash = PasswordField('Verify Password', validators=[DataRequired()])
    profile_pic = FileField('Profile Pic')
    submit = SubmitField('Submit')

# Create a Name Form
class NameForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField('Submit')

# Create a Password Form
class PasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Create a Posts Form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    # content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()] )
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
# Login Form
class LoginForm(FlaskForm):
    user_name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
# Search Form
class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Submit')

    # BooleanField
		# DateField
		# DateTimeField
		# DecimalField
		# FileField
		# HiddenField
		# MultipleField
		# FieldList
		# FloatField
		# FormField
		# IntegerField
		# PasswordField
		# RadioField
		# SelectField
		# SelectMultipleField
		# SubmitField
		# StringField
		# TextAreaField

		## Validators
		# DataRequired
		# Email
		# EqualTo
		# InputRequired
		# IPAddress
		# Length
		# MacAddress
		# NumberRange
		# Optional
		# Regexp
		# URL
		# UUID
		# AnyOf
		# NoneOf