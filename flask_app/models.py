from flask import current_app
from flask_login import UserMixin
from . import login_manager
from . import config

import os, sqlite3
from sqlite3 import Error

@login_manager.user_loader
def load_user(username):
    conn = None
    try:
        conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
        c = conn.cursor()
        c.execute("SELECT username, password, level from users where username = (?)", [username])
        user = c.fetchone()
        conn.close()
        return User(user[0], user[1], user[2])
    except Error as e:
        if conn:
            conn.close()
        return None

class User(UserMixin):
    def __init__(self, username, password, level):
        self.username = username
        self.password = password
        self.level = level

    def get_id(self):
        return self.username

class Tag():
    def __init__(self, tag, category):
        self.tag = tag
        self.category = category

class File():
    def __init__(self, file_id, folder_id, name, tags):
        self.file_id = file_id
        self.folder_id = folder_id
        self.name = name
        self.tags = tags

class Folder():
    def __init__(self, folder_id, name):
        self.folder_id = folder_id
        self.name = name