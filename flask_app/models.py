from flask_login import UserMixin
from . import db, login_manager

@login_manager.user_loader
def load_user(username):
    return User.objects(username=username).first()

class Tag(db.Document):
    tag = db.StringField(required=True, unique=True)
    category = db.StringField(required=True)

class File(db.Document):
    file_id = db.StringField(required=True)
    folder_id = db.StringField(required=True)
    name = db.StringField(required=True)
    tags = db.ListField(db.ReferenceField(Tag, required=True))
    description = db.StringField()

class Folder(db.Document):
    folder_id = db.StringField(required=True)
    parent_id = db.StringField()
    name = db.StringField(required=True)
    description = db.StringField()

# level - 0: root, 1: admin, 2: mod, 3: user
class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    level = db.IntField(required=True)
    api_key = db.StringField()
    favorites = db.ListField(db.ReferenceField(File, required=True))

    def get_id(self):
        return self.username

class Metadata():
    def __init__(self, url=None, description=None, image=None, title=None):
        self.title = title
        self.url = url
        self.description = description
        self.image = image