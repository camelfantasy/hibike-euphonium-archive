from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    Blueprint,
    session,
    g,
)
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

import io
import base64

from . import bcrypt
from .forms import (
    SearchForm,
    LoginForm,
)
from .models import User, load_user

main = Blueprint("main", __name__)