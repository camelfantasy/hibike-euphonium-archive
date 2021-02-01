from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from flask_mongoengine import MongoEngine
import os

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()

from flask_app.users.routes import users
from flask_app.results.routes import results
from .forms import SearchForm
from .models import User

def initialize_root_user():
    try:
        if not User.objects(username="root").first():
            hashed = bcrypt.generate_password_hash("password").decode("utf-8")
            user = User(username="root", password=hashed, level=0)
            user.save()
        return 0
    except:
        print("\033[91mMongoEngine error, startup unsuccessful\033[0m")
        return 1

def page_not_found(e):
    return render_template("404.html", searchform=SearchForm()), 404

def create_app(test_config=None):
    app = Flask(__name__)
        
    print("Getting config values from config.py")
    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    print("Getting config values from environment")
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

    print("Initializing login manager")
    login_manager.init_app(app)
    print("Initializing bcrypt")
    bcrypt.init_app(app)

    print("Initializing MongoDB")
    db.init_app(app)
    print("Initializing root user")
    if initialize_root_user() == 1:
        return None

    csp = {
        'default-src': ['\'self\'','stackpath.bootstrapcdn.com','code.jquery.com','cdn.jsdelivr.net',
            'cdnjs.cloudflare.com','drive.google.com','*.googleusercontent.com','\'unsafe-inline\''],
        'img-src': ['\'self\' data: *']
    }
    print("Initializing Talisman")
    Talisman(app, content_security_policy=csp)

    print("Registering blueprints")
    app.register_blueprint(results)
    app.register_blueprint(users)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    print('\033[92mStartup successful\033[0m')
    return app
