from flask_login import UserMixin
from . import db, login_manager
from . import config

@login_manager.user_loader
def load_user(username):
    return User.objects(username=username).first()

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)

    def get_id(self):
        return self.username