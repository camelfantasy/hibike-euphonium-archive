from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo

class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100, message="Query must be under 100 characters.")]
    )
    submit_btn = SubmitField("Search")

class AddTagForm(FlaskForm):
    tag = StringField("Add tag", validators=[InputRequired()])
    category = SelectField("Category", choices=[("Characters", "Characters"), ("Media", "Media"), ("Other", "Other")])
    file_id = StringField("File ID")
    submit_btn = SubmitField("Add")

class DeleteTagForm(FlaskForm):
    tag = StringField("Tag", validators=[InputRequired()])
    file_id = StringField("File ID")
    submit_btn = SubmitField("Delete")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=1, max=20, message="Login failed. Check your username and/or password")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=1, max=50)])
    submit_btn = SubmitField("Login")

class UpdatePasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[InputRequired(), Length(min=8, max=50, message="Password must be 8-50 characters.")])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit_btn = SubmitField("Change Password")

class AddUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=1, max=20, message="Username must be 1-20 characters.")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=50, message="Password must be 8-50 characters.")])
    level = SelectField("Level", choices=[(2, "User"), (1, "Admin")])
    submit_btn = SubmitField("Add")

class DeleteUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    submit_btn = SubmitField("Delete")

class ChangeAPIKeyForm(FlaskForm):
    submit_btn = SubmitField("Change")

class UpdateDescriptionForm(FlaskForm):
    description = TextAreaField("Description")
    file_id = StringField("File ID")
    submit_btn = SubmitField("Save")