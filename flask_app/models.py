from flask_login import UserMixin
from mongoengine.queryset.visitor import Q
from . import db, login_manager

@login_manager.user_loader
def load_user(username):
    return User.objects(username=username).first()

class Tag(db.Document):
    tag = db.StringField(required=True, unique=True)
    category = db.StringField(required=True)

    def dictToObject(tag):
        return Tag(id=tag['_id'], tag=tag['tag'], category=tag['category'])

class File(db.Document):
    file_id = db.StringField(required=True)
    folder_id = db.StringField(required=True)
    name = db.StringField(required=True)
    tags = db.ListField(db.ReferenceField(Tag, required=True))
    description = db.StringField()

    def dictToObject(file):
        tags = [Tag.dictToObject(x) for x in file['tags']]
        return File(id=file['_id'], file_id=file['file_id'], folder_id=file['folder_id'], name=file['name'], tags=tags, description=file['description'])

    def objectsDereferencedTags():
        db_query = [
            {
                "$unwind": "$tags"
            },
			{
                "$lookup":
                {
                    "from": "tag",
                    "localField": "tags",
                    "foreignField": "_id",
                    "as": "tags"
                }
			},
			{
                "$group":
                {
                    "_id": "$_id",
                    "file_id": {"$first": "$file_id"},
                    "folder_id": {"$first": "$folder_id"},
                    "name": {"$first": "$name"},
                    "tags": {"$push": {"$first": "$tags"}},
                    "description": {"$first": "$description"}
			    }
			}
		]

        files_with_tags = list(File.objects.aggregate(*db_query))
        files_without_tags = list(File.objects(Q(tags__exists=False) | Q(tags__size=0)))
        return files_without_tags + [File.dictToObject(x) for x in files_with_tags]

    def deleteTagIdFromAllFiles(id):
        find_query = { "tags": { "$in": [id] } }
        update_query = { "$pull": { "tags": id } }
        return File.objects(__raw__=find_query).update(__raw__=update_query)

    def bulkAddTagIdToFiles(id, files):
        find_query = {
            "$and":
            [
                { "tags": { "$nin": [id] } },
                { "_id": { "$in": [x.id for x in files] } }
            ]
        }
        update_query = { "$addToSet": { "tags": id } }
        return File.objects(__raw__=find_query).update(__raw__=update_query)

    def bulkDeleteTagIdFromFiles(id, files):
        find_query = {
            "$and":
            [
                { "tags": { "$in": [id] } },
                { "_id": { "$in": [x.id for x in files] } }
            ]
        }
        update_query = { "$pull": { "tags": id } }
        return File.objects(__raw__=find_query).update(__raw__=update_query)

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

    def bulkDeleteFavoriteIdsFromAllUsers(ids):
        find_query = { "favorites": { "$in": ids } }
        update_query = { "$pull": { "favorites": { "$in": ids } } }
        User.objects(__raw__=find_query).update(__raw__=update_query)

class Metadata():
    def __init__(self, url=None, description=None, image=None, title=None):
        self.title = title
        self.url = url
        self.description = description
        self.image = image