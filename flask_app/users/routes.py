from flask import Blueprint, redirect, url_for, render_template, flash, request, session, current_app
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
from ..forms import SearchForm, UpdatePasswordForm, LoginForm, AddUserForm, DeleteUserForm
from ..models import User

import os, sqlite3
from sqlite3 import Error

from google.oauth2 import service_account
import googleapiclient.discovery

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

            flash("Password changed.", "top-success")
        except Error as e:
            flash("Server error.", "top-warning")
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
                flash("User '" + username + "' added.", "bottom-success")
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
                flash("User '" + username + "' deleted.", "bottom-success")
        except Error as e:
            flash("Server error.", "bottom-warning")
        finally:
            if conn:
                conn.close()

            return redirect(url_for("users.account"))

    conn = None
    users = []
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
    if current_user.is_authenticated and current_user.level < 2:
        files, folders = getfiles()
        if files == None:
            return "1", 200
        success = update(files, folders)
        return success, 200
    return "1", 200

def getfiles():
    try:
        service = googleapiclient.discovery.build('drive', 'v3', developerKey=current_app.config['DRIVE_API_KEY'])
        ids = [current_app.config['ROOT_ID']]
        ret_files = []
        ret_folders = [("\"" + ids[0] + "\"", "\"\"", "\"Hibike! Series\"")]
        while len(ids) != 0:
            current_folder = ids.pop(0)
            param = {"q": "'" + current_folder + "' in parents", "fields":"files(id, mimeType, description, name)"}
            result = service.files().list(**param).execute()
            files = result.get('files')

            for afile in files:
                if afile.get('mimeType') == 'application/vnd.google-apps.folder':
                    tup = map(lambda x:"\"" + x + "\"",(afile.get('id'), current_folder, afile.get('name')))
                    ret_folders.append(tup)
                    ids.append(afile.get('id'))
                elif 'image' in afile.get('mimeType'):
                    desc = afile.get('description') if afile.get('description') else ""
                    tup = map(lambda x:"\"" + x + "\"",(afile.get('id'), current_folder, afile.get('name'), desc))
                    ret_files.append(tup)
        
        return ret_files, ret_folders
    except Error as e:
        return None, None

def update(files, folders):
    query_files = ",".join(map(lambda x:"(" + ",".join(x) + ")", files))
    query_folders = ",".join(map(lambda x:"(" + ",".join(x) + ")", folders))

    success = "0"
    conn = None
    try:
        conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
        c = conn.cursor()
        c.execute("DELETE FROM file_ids")
        c.execute("INSERT INTO file_ids(file_id, folder_id, name, tags) values" + query_files)
        c.execute("DELETE FROM folder_ids")
        c.execute("INSERT INTO folder_ids(folder_id, parent_id, name) values" + query_folders)
        conn.commit()
    except Error as e:
        print(e)
        success = "1"
    finally:
        if conn:
            conn.close()

    return success