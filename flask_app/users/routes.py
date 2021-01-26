from flask import Blueprint, redirect, url_for, render_template, flash, request, session
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
from ..forms import SearchForm, UpdatePasswordForm, LoginForm
from ..models import User

users = Blueprint("users", __name__)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()
    if form.validate_on_submit():
        # user = User.objects(username=form.username.data).first()

        # if user is not None and bcrypt.check_password_hash(
        #     user.password, form.password.data
        # ):
        #     login_user(user)
        #     return redirect(url_for("results.index"))
        # else:
        #     flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Admin Login", form=form, searchform=SearchForm())

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("results.index"))

@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    password_form = UpdatePasswordForm()
    
    if password_form.validate_on_submit() and current_user.is_authenticated:
            # hashed = bcrypt.generate_password_hash(password_form.password.data).decode("utf-8")
            # current_user.modify(password=hashed)
            # current_user.save()
            # flash("Password updated")
            return redirect(url_for("users.account"))

    return render_template(
        "account.html",
        title="Admin",
        password_form=password_form
    )

# bypasses login for testing html only
@users.route("/test", methods=["GET", "POST"])
def test():
    return render_template("account.html", title="Admin", searchform=SearchForm(), password_form=UpdatePasswordForm())