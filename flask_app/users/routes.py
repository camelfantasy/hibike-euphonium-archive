from flask import Blueprint, redirect, url_for, render_template, flash, request, session
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
from ..forms import SearchForm, UpdatePasswordForm, LoginForm
from ..models import User

import os
import sqlite3
from sqlite3 import Error

users = Blueprint("users", __name__)
path = os.getcwd() + r"/flask_app/files/pythonsqlite.db"

@users.route("/login", methods=["GET", "POST"])
def login():
    print(current_user)
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()
    if form.validate_on_submit():
        conn = None

        try:
            conn = sqlite3.connect(path)
            c = conn.cursor()
            c.execute('select id, username, password from users where username=?', [form.username.data])
            u = c.fetchone()

            if u is not None and bcrypt.check_password_hash(u[2], form.password.data):
                user = User(u[1], u[2])
                login_user(user)
            else:
                flash("Login failed. Check your username and/or password.")
        except Error as e:
            flash("Server error.")
        finally:
            if conn:
                conn.close()
                
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Admin Login", form=form, searchform=SearchForm())

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("users.login"))

@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    password_form = UpdatePasswordForm()

    if password_form.validate_on_submit() and current_user.is_authenticated:
        hashed = bcrypt.generate_password_hash(password_form.password.data).decode("utf-8")
        conn = None

        try:
            conn = sqlite3.connect(path)
            c = conn.cursor()
            c.execute('update users set password=? where username=?', (hashed, current_user.username))
            conn.commit()

            flash("Password changed.")
        except Error as e:
            flash("Server error.")
        finally:
            if conn:
                conn.close()

            return redirect(url_for("users.account"))

    return render_template("account.html", title="Admin", searchform=SearchForm(), password_form=password_form, username=current_user.username)

@users.route("/sync")
@login_required
def sync():
    return "0", 200