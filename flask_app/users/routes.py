from flask import Blueprint, redirect, url_for, render_template, flash, request, session, current_app
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
from ..forms import SearchForm, UpdatePasswordForm, LoginForm, AddUserForm, DeleteUserForm
from ..models import User, File, Folder

import googleapiclient.discovery

users = Blueprint("users", __name__)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
        else:
            flash("Login failed. Check your username and/or password.")
        
        return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form, searchform=SearchForm())

@users.route("/logout")
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
        current_user.modify(password=hashed)
        current_user.save()
        flash("Password changed.", "top-success")
        return redirect(url_for("users.account"))

    if request.form.get('submit') == 'Add' and add_form.validate_on_submit() and current_user.is_authenticated \
        and current_user.level < 2 and current_user.level < int(add_form.level.data):

        hashed = bcrypt.generate_password_hash(add_form.password.data).decode("utf-8")
        username = add_form.username.data

        if User.objects(username=add_form.username.data).first():
            flash("User '" + username + "' already exists.", "bottom-warning")
        else:
            user = User(username=username, password=hashed, level=add_form.level.data)
            user.save()
            flash("User '" + username + "' added.", "bottom-success")

        return redirect(url_for("users.account"))

    if request.form.get('submit') == 'Delete' and delete_user_form.validate_on_submit() and current_user.is_authenticated \
        and current_user.level < 2:

        username = delete_user_form.username.data
        user = User.objects(username=delete_user_form.username.data).first()
        if user is None:
            flash("User '" + username + "' does not exist.", "bottom-warning")
        elif current_user.level <= user.level:
            user.delete()
            flash("User '" + username + "' deleted.", "bottom-success")
            

        return redirect(url_for("users.account"))

    users = list(User.objects())
    users.sort(key=lambda x: (x.level, x.username.lower()))

    return render_template("account.html", title="Account", searchform=SearchForm(),
        password_form=password_form, addform=add_form, deleteuserform=delete_user_form, users=users)

@users.route("/sync")
def sync():
    if current_user.is_authenticated and current_user.level < 2:
        files, folders = getfiles()
        if files == None:
            return "1", 200
        success = update(files, folders)
        return success, 200
    return render_template("404.html", searchform=SearchForm()), 404

def getfiles():
    try:
        file_dict = { i.file_id : i.tags for i in File.objects() }
        current_folders = Folder.objects()

        service = googleapiclient.discovery.build('drive', 'v3', developerKey=current_app.config['DRIVE_API_KEY'])
        ids = [current_app.config['ROOT_ID']]
        ret_files = []
        ret_folders = [Folder(folder_id=ids[0], parent_id="", name="Hibike! Series")]

        while len(ids) != 0:
            current_folder = ids.pop(0)
            param = {"q": "'" + current_folder + "' in parents", "fields":"files(id, mimeType, name)"}
            result = service.files().list(**param).execute()
            files = result.get('files')

            for afile in files:
                if afile.get('mimeType') == 'application/vnd.google-apps.folder':
                    ret_folders.append(Folder(folder_id=afile.get('id'), parent_id=current_folder, name=afile.get('name')))
                    ids.append(afile.get('id'))
                elif 'image' in afile.get('mimeType'):
                    tags = file_dict[afile.get('id')] if afile.get('id') in file_dict else None
                    ret_files.append(File(file_id=afile.get('id'), folder_id=current_folder, name=afile.get('name'), tags=tags))
        
        return ret_files, ret_folders
    except:
        return None, None

def update(files, folders):
    success = "0"
    try:
        File.objects.delete()
        File.objects.insert(files)
        Folder.objects.delete()
        Folder.objects.insert(folders)
    except:
        success = "1"

    return success