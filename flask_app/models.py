from flask_login import UserMixin
from . import login_manager
from . import config

import os
import sqlite3
from sqlite3 import Error

@login_manager.user_loader
def load_user(username):
    conn = None
    try:
        conn = sqlite3.connect(os.getcwd() + r"/flask_app/files/pythonsqlite.db")
        c = conn.cursor()
        c.execute("SELECT username, password from users where username = (?)", [username])
        user = c.fetchone()
        conn.close()
        return User(user[0], user[1])
    except Error as e:
        if conn:
            conn.close()
        return None

class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_id(self):
        return self.username