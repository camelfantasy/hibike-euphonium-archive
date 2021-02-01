from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    EqualTo,
    ValidationError,
)

class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100, message="Query must be under 100 characters.")]
    )
    submit = SubmitField("Search")

class AddTagForm(FlaskForm):
    tag = StringField("Add tag:", validators=[InputRequired()])
    category = SelectField("Category:", choices=[("Characters", "Characters"), ("Media", "Media"), ("Other", "Other")])
    submit = SubmitField("Add")

class DeleteTagForm(FlaskForm):
    tag = StringField("Tag", validators=[InputRequired()])
    submit = SubmitField("Delete")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=1, max=20, message="Login failed. Check your username and/or password")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=1, max=50)])
    submit = SubmitField("Login")

class UpdatePasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=50, message="Password must be 8-50 characters.")])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Update Password")

class AddUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=1, max=20, message="Username must be 1-20 characters.")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=50, message="Password must be 8-50 characters.")])
    level = SelectField("Level", choices=[(2, "User"), (1, "Admin")])
    submit = SubmitField("Add")

class DeleteUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    submit = SubmitField("Delete")