from flask import Blueprint, redirect, url_for, render_template, flash, request, current_app
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt, hashing
from ..forms import SearchForm, UpdatePasswordForm, LoginForm, RegisterForm, ChangeUserLevelForm, DeleteUserForm, SubmitForm
from ..models import User, File, Folder, Tag, Metadata

import googleapiclient.discovery
import secrets
import threading
import re

users = Blueprint("users", __name__)
syncing = False
last_sync = 0
levels = {3:"User", 2:"Mod", 1:"Admin", 0:"Root"}

def getSearchTags():
	tags = list(map(lambda x: x.tag, Tag.objects()))
	tags.sort(key=lambda x:x.lower())
	return tags

# viewpoints below

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

	metadata = Metadata(title="Login", description="")
	return render_template("login.html", title="Login", form=form, searchform=SearchForm(),
		searchtags=getSearchTags(), metadata=metadata)

@users.route("/register", methods=["GET", "POST"])
def register():
	if current_user.is_authenticated:
		return redirect(url_for("users.account"))

	form = RegisterForm()
	if form.validate_on_submit():
		regex = re.compile("^" + form.username.data.strip() + "$", re.IGNORECASE)
		if User.objects(username=regex).first():
			flash("Username taken. Please choose another.")
		else:
			hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
			username = form.username.data.strip()
			user = User(username=username, password=hashed, level=3, api_key=None, favorites=[])
			user.save()
			login_user(user)
			flash("Account created.", "top-success")
		
		return redirect(url_for("users.register"))

	metadata = Metadata(title="Register", description="")
	return render_template("register.html", title="Register", form=form,
		searchform=SearchForm(), searchtags=getSearchTags(), metadata=metadata)

@users.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("users.login"))

@users.route("/delete")
@login_required
def delete():
	if current_user.level > 0:
		user = User.objects(username=current_user.username).first()
		logout_user()
		user.delete()
		flash("Account deleted.", "success")
		return redirect(url_for("users.login"))
	
	return redirect(url_for("users.account"))

@users.route("/account", methods=["GET"])
@login_required
def account():
	users = list(User.objects())
	users.sort(key=lambda x: (x.level, x.username.lower()))

	metadata = Metadata(title="Account", description="")
	return render_template("account.html", title="Account", searchform=SearchForm(),
		password_form=UpdatePasswordForm(), deleteuserform=DeleteUserForm(),
		changeuserlevelform=ChangeUserLevelForm(), submitform=SubmitForm(),
		users=users, levels=levels, searchtags=getSearchTags(), metadata=metadata)

@users.route("/favorites", methods=["GET"])
@login_required
def favorites():
	results = list(current_user.favorites)
	results.sort(key=lambda x:(x.folder_id, x.name.lower()))
	results_matrix = [results[i:i + 4] for i in range(0, len(results), 4)]
	initial_results = results_matrix[:10]
	remaining_results = list(map(lambda x: list(map(lambda y: y.file_id, x)),results_matrix[10:]))
	
	return render_template("favorites.html", title="Favorites", searchform=SearchForm(),
		submitform=SubmitForm(), searchtags=getSearchTags(), results=initial_results,
		remaining_results=remaining_results, num_results=len(results))

# ajax routes and helpers below

@users.route("/replace_api_key", methods=["POST"])
def replace_api_key():
	submitform = SubmitForm()

	if submitform.validate_on_submit() and current_user.is_authenticated and current_user.level < 3:
		new_key = secrets.token_urlsafe(24)
		current_user.modify(api_key=hashing.hash_value(new_key))
		current_user.save()
		return new_key, 200

	return render_template("404.html", title="404", searchform=SearchForm(), searchtags=getSearchTags())

@users.route("/delete_api_key", methods=["POST"])
def delete_api_key():
	submitform = SubmitForm()

	if submitform.validate_on_submit() and current_user.is_authenticated and current_user.level < 3:
		current_user.modify(api_key=None)
		current_user.save()
		return "0", 200

	return render_template("404.html", title="404", searchform=SearchForm(), searchtags=getSearchTags())

@users.route("/change_password", methods=["POST"])
def change_password():
	updatepasswordform = UpdatePasswordForm()
	if current_user.is_authenticated:
		if updatepasswordform.validate_on_submit():
			hashed = bcrypt.generate_password_hash(updatepasswordform.password.data).decode("utf-8")
			current_user.modify(password=hashed)
			current_user.save()
			return {'success':0, 'message':'Password changed.'}, 200
		else:
			error = updatepasswordform.password.errors if updatepasswordform.password.errors else updatepasswordform.confirm_password.errors
			return {'success':1, 'message':error}, 200

	return render_template("404.html", title="404", searchform=SearchForm(), searchtags=getSearchTags())

@users.route("/change_level", methods=["POST"])
def change_level():
	changeuserlevelform = ChangeUserLevelForm()
	user = User.objects(username=changeuserlevelform.username.data).first()
	new_level = int(changeuserlevelform.level.data) if changeuserlevelform.level else None

	if current_user.is_authenticated and changeuserlevelform.validate_on_submit() and user \
		and current_user.level < user.level and current_user.level < new_level:

		message = '"' + user.username + '" changed from ' + levels[user.level] + ' to '  + levels[new_level] + '.'
		user.modify(level=new_level)
		user.save()
		return {'success':0, 'message':message}, 200

	return render_template("404.html", title="404", searchform=SearchForm(), searchtags=getSearchTags())

@users.route("/delete_user", methods=["POST"])
def delete_user():
	deleteuserform = DeleteUserForm()
	user = User.objects(username=deleteuserform.username.data).first()

	if current_user.is_authenticated and deleteuserform.validate_on_submit() and user and current_user.level < user.level:
		message = '"' + user.username + '" deleted.'
		user.delete()
		return {'success':0, 'message':message}, 200

	return render_template("404.html", title="404", searchform=SearchForm(), searchtags=getSearchTags())

# 0: success, 1: failed, 2: sync started, 3: another sync in progress
@users.route("/sync", methods=["POST"])
def sync():
	submitform = SubmitForm()
	
	if submitform.validate_on_submit() and current_user.is_authenticated and current_user.level < 2:
		global syncing
		if syncing:
			return "3", 200
		else:
			syncing = True
			thread = threading.Thread(target=sync_pipeline, kwargs={'config': current_app.config})
			thread.daemon = True
			thread.start()
			return "2", 200

	return render_template("404.html", title="404", searchform=SearchForm(), searchtags=getSearchTags())

def sync_pipeline(config):
	global syncing
	global last_sync

	result = getfiles(config)
	if result is not None:
		last_sync = update(result[0], result[1], result[2])
	else:
		last_sync = 1
	syncing = False

def getfiles(config):
	try:
		# preserve tags through file deletion
		file_dict = { i.file_id : [i.tags, i.description, i.id] for i in File.objects() }
		folder_dict = { i.folder_id : [i.description, i.id] for i in Folder.objects() }

		service = googleapiclient.discovery.build('drive', 'v3', developerKey=config['DRIVE_API_KEY'])
		ids = [config['ROOT_ID']]
		ret_files = []
		ret_folders = []

		# get root folder name
		param = {"fileId": ids[0], "fields":"name"}
		result = service.files().get(**param).execute()
		root_name = result.get('name')
		ret_folders.append(Folder(folder_id=ids[0], parent_id="", name=root_name))

		# traverses folder structure breadth-first
		while len(ids) != 0:
			current_folder = ids.pop(0)
			param = {"q": "'" + current_folder + "' in parents", "fields":"files(id, mimeType, name)", "pageSize":"1000"}
			result = service.files().list(**param).execute()
			files = result.get('files')
			
			for afile in files:
				if afile.get('mimeType') == 'application/vnd.google-apps.folder':
					if afile.get('id') in folder_dict:
						info = folder_dict[afile.get('id')]
						ret_folders.append(Folder(id=info[1], folder_id=afile.get('id'), parent_id=current_folder,
							name=afile.get('name'), description=info[0]))
					else:
						ret_folders.append(Folder(folder_id=afile.get('id'), parent_id=current_folder,
							name=afile.get('name'), description=None))
					ids.append(afile.get('id'))
				elif 'image' in afile.get('mimeType'):
					if afile.get('id') in file_dict:
						info = file_dict[afile.get('id')]
						ret_files.append(File(id=info[2], file_id=afile.get('id'), folder_id=current_folder,
							name=afile.get('name'), tags=info[0], description=info[1]))
					else:
						ret_files.append(File(file_id=afile.get('id'), folder_id=current_folder,
							name=afile.get('name'), tags=[], description=None))
		
		deleted_ids = set([x[2] for x in list(file_dict.values())]).difference(set([x.id for x in ret_files]))
		return ret_files, ret_folders, deleted_ids
	except:
		return None, None, None

def update(files, folders, deleted_ids):
	success = "0"
	try:
		File.objects.delete()
		File.objects.insert(files)
		Folder.objects.delete()
		Folder.objects.insert(folders)

		# get users with deleted files and remove
		users = User.objects().filter(favorites__in=deleted_ids)
		for user in users:
			user.favorites = [x for x in user.favorites if x.id not in deleted_ids]
			user.save()
	except:
		success = "1"

	return success

@users.route("/sync_progress", methods=["GET"])
def sync_progress():
	if current_user.is_authenticated and current_user.level < 2:
		return {'syncing': syncing, 'last_sync': last_sync}, 200
	else:
		return render_template("404.html", title="404", searchform=SearchForm(), searchtags=getSearchTags())