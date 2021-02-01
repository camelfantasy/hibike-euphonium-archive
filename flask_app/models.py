from flask import current_app
from flask_login import UserMixin
from . import db, login_manager, config

@login_manager.user_loader
def load_user(username):
    return User.objects(username=username).first()

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    level = db.IntField(required=True)

    def get_id(self):
        return self.username

class Tag(db.Document):
    tag = db.StringField(required=True, unique=True)
    category = db.StringField(required=True)

class File(db.Document):
    file_id = db.StringField(required=True)
    folder_id = db.StringField(required=True)
    name = db.StringField(required=True)
    tags = db.ListField(db.ReferenceField(Tag, required=True))

class Folder(db.Document):
    folder_id = db.StringField(required=True)
    parent_id = db.StringField()
    name = db.StringField(required=True)