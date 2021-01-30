from flask import Blueprint, redirect, url_for, render_template, flash, request, session, current_app
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
from ..forms import SearchForm, UpdatePasswordForm, LoginForm, AddUserForm, DeleteUserForm
from ..models import User

import os, sqlite3
from sqlite3 import Error

users = Blueprint("users", __name__)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()
    if form.validate_on_submit():
        conn = None
        try:
            conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
            c = conn.cursor()
            c.execute('select username, password, level from users where username=?', [form.username.data])
            u = c.fetchone()

            if u is not None and bcrypt.check_password_hash(u[1], form.password.data):
                user = User(u[0], u[1], u[2])
                login_user(user)
            else:
                flash("Login failed. Check your username and/or password.")
        except Error as e:
            flash("Server error.")
        finally:
            if conn:
                conn.close()
                
            return redirect(url_for("users.login"))

    return render_template("login.html", title="User Login", form=form, searchform=SearchForm())

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("users.login"))

@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    password_form = UpdatePasswordForm()
    add_form = AddUserForm()
    delete_user_form = DeleteUserForm()

    if request.form.get('submit') == 'Update Password' and password_form.validate_on_submit() and current_user.is_authenticated:
        hashed = bcrypt.generate_password_hash(password_form.password.data).decode("utf-8")
        
        conn = None
        try:
            conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
            c = conn.cursor()
            c.execute('update users set password=? where username=?', (hashed, current_user.username))
            conn.commit()

            flash("Password changed.", "top-info")
        except Error as e:
            flash("Server error.", "top-alert")
        finally:
            if conn:
                conn.close()

            return redirect(url_for("users.account"))

    if request.form.get('submit') == 'Add' and add_form.validate_on_submit() and current_user.is_authenticated \
        and current_user.level < 2 and current_user.level < int(add_form.level.data):
        conn = None
        try:
            hashed = bcrypt.generate_password_hash(add_form.password.data).decode("utf-8")
            username = add_form.username.data

            conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
            c = conn.cursor()
            c.execute("SELECT * from users where username=?", [username])
            if c.fetchone() is None:
                c.execute('INSERT INTO users(username, password, level) values(?, ?, ?)', (username, hashed, add_form.level.data))
                conn.commit()
                flash("User added.", "bottom-info")
            else:
                flash("User '" + username + "' already exists.", "bottom-warning")
        except Error as e:
            flash("Server error.", "bottom-warning")
        finally:
            if conn:
                conn.close()

            return redirect(url_for("users.account"))

    if request.form.get('submit') == 'Delete' and delete_user_form.validate_on_submit() and current_user.is_authenticated \
        and current_user.level < 2:
        conn = None
        try:
            username = delete_user_form.username.data

            conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
            c = conn.cursor()
            c.execute("SELECT username,level from users where username=?", [username])
            user = c.fetchone()
            if user is None:
                flash("User '" + username + "' does not exist.", "bottom-warning")
            elif current_user.level < user[1]:
                c.execute('DELETE FROM users where username=?', [username])
                conn.commit()
                flash("User deleted.", "bottom-info")
        except Error as e:
            flash("Server error.", "bottom-warning")
        finally:
            if conn:
                conn.close()

            return redirect(url_for("users.account"))

    try:
        conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
        c = conn.cursor()
        c.execute('select username, level from users')
        result = c.fetchall()
        users = list(map(lambda x: User(x[0], "", x[1]), result))
        users.sort(key=lambda x: (x.level, x.username.lower()))
    except Error as e:
        flash("Server error.", "top-warning")
    finally:
        if conn:
            conn.close()

    return render_template("account.html", title="Admin", searchform=SearchForm(),
        password_form=password_form, addform=add_form, deleteuserform=delete_user_form, users=users)

@users.route("/sync")
@login_required
def sync():
    # code
    return "0", 200