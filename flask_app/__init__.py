from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_talisman import Talisman
from flask_mongoengine import MongoEngine
import os

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()

from .routes import main
from flask_app.users.routes import users
from flask_app.results.routes import results
from .forms import SearchForm
from .models import User

def initialize_root_user():
    if not User.objects(username="root").first():
        hashed = bcrypt.generate_password_hash("password").decode("utf-8")
        user = User(username="root", password=hashed, level=0)
        user.save()

def page_not_found(e):
    return render_template("404.html", searchform=SearchForm()), 404

def create_app(test_config=None):
    app = Flask(__name__)
        
    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    secret_key = os.getenv("SECRET_KEY")
    if secret_key and not app.config["SECRET_KEY"]:
        app.config["SECRET_KEY"] = secret_key.encode('utf_8')

    drive_api_key = os.getenv("DRIVE_API_KEY")
    if drive_api_key and not app.config["DRIVE_API_KEY"]:
        app.config["DRIVE_API_KEY"] = drive_api_key

    root_id = os.getenv("ROOT_ID")
    if root_id and not app.config["ROOT_ID"]:
        app.config["ROOT_ID"] = root_id

    mongodb_host = os.getenv("MONGODB_HOST")
    if mongodb_host and not app.config["MONGODB_HOST"]:
        app.config["MONGODB_HOST"] = mongodb_host

    login_manager.init_app(app)
    bcrypt.init_app(app)

    db.init_app(app)
    initialize_root_user()

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
