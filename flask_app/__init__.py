from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_talisman import Talisman
import os
import sqlite3
from sqlite3 import Error

login_manager = LoginManager()
bcrypt = Bcrypt()

from .routes import main
from flask_app.users.routes import users
from flask_app.results.routes import results
from .forms import SearchForm

def page_not_found(e):
    return render_template("404.html", searchform=SearchForm()), 404

def initialize_sqlite(sqlite_path):
    db_file = os.getcwd() + sqlite_path
    conn = None
    try:
        conn = sqlite3.connect(db_file)

        query_users = """CREATE TABLE IF NOT EXISTS users (
            id integer PRIMARY KEY,
            username text NOT NULL UNIQUE,
            password text NOT NULL,
            level integer NOT NULL
        );"""

        query_tags = """CREATE TABLE IF NOT EXISTS tags (
            id integer PRIMARY KEY,
            tag text NOT NULL,
            category text NOT NULL
        );"""

        query_file_ids = """CREATE TABLE IF NOT EXISTS file_ids (
            id integer PRIMARY KEY,
            file_id text NOT NULL,
            folder_id text NOT NULL,
            tags text NOT NULL
        );"""

        query_folder_ids = """CREATE TABLE IF NOT EXISTS folder_ids (
            id integer PRIMARY KEY,
            folder_id text NOT NULL,
            parent_id text NOT NULL,
            name text NOT NULL
        );"""

        password = bcrypt.generate_password_hash("password").decode("utf-8")
        query_create_root = """INSERT OR IGNORE INTO users(username, password, level)
            VALUES ("root", ?, 0)
        ;"""
        
        c = conn.cursor()
        c.execute(query_users)
        c.execute(query_tags)
        c.execute(query_file_ids)
        c.execute(query_folder_ids)
        c.execute(query_create_root, [password])
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def create_app(test_config=None):
    app = Flask(__name__)
        
    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    secret_key = os.getenv("SECRET_KEY")
    if secret_key:
        app.config["SECRET_KEY"] = secret_key.encode('utf_8')

    drive_api_key = os.getenv("DRIVE_API_KEY")
    if drive_api_key:
        app.config["DRIVE_API_KEY"] = drive_api_key

    root_id = os.getenv("ROOT_ID")
    if root_id:
        app.config["ROOT_ID"] = root_id

    login_manager.init_app(app)
    bcrypt.init_app(app)

    initialize_sqlite(app.config["SQLITE_PATH"])

    csp = {
        'default-src': ['\'self\'','stackpath.bootstrapcdn.com','code.jquery.com','cdn.jsdelivr.net','cdnjs.cloudflare.com','\'unsafe-inline\''],
        'img-src': ['\'self\' data: *']
    }

    Talisman(app, content_security_policy=csp)

    app.register_blueprint(main)
    app.register_blueprint(results)
    app.register_blueprint(users)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app
