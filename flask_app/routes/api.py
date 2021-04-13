from flask import Blueprint, redirect, url_for, current_app, jsonify, request
from ..models import File, Folder, Tag, User
from ..api_models import API_Tag, API_File, API_File_No_Tags, API_Folder
from .. import bcrypt, pymongo
import re

api = Blueprint("api", __name__)

# routes for all users below
@api.route("/api/v1/tags", methods=["GET"])
def tags():
    tags = list(Tag.objects())
    tags.sort(key=lambda x:x.tag.lower())
    tags = list(map(lambda x: API_Tag(tag=x.tag, category=x.category).__dict__, tags))
    return jsonify(tags)

@api.route("/api/v1/all_images/<page>", methods=["GET"])
def all_images(page):
    size = File.objects.count()
    
    try:
        page = int(page)
    except:
        return "Not an integer", 400
    
    if page < 1:
        return "Page number must be at least 1", 400
    elif size == 0:
        return "No images", 400
    elif (page-1)*100 > size:
        return "No more pages", 400

    images = File.objects.skip((page-1)*100).limit(100)
    ret = []

    for image in images:
        tags = list(map(lambda x: API_Tag(tag=x.tag, category=x.category).__dict__, image.tags))
        ret.append(API_File(file_id=image.file_id, folder_id=image.folder_id,
            name=image.name, tags=tags, description=image.description).__dict__)

    return jsonify(ret)

@api.route("/api/v1/tag_images", methods=["GET"])
def tag_images():
    if not request.args.get('tag'):
        return "Missing tag parameter", 400

    regex = re.compile("^" + request.args.get('tag').strip() + "$", re.IGNORECASE)
    tag = Tag.objects(tag=regex).first()

    if not tag:
        return "Tag does not exist", 400
    
    images = File.objects().filter(tags__contains=tag.id)
    images = list(map(lambda x: API_File_No_Tags(file_id=x.file_id, folder_id=x.folder_id,
            name=x.name, description=x.description).__dict__, images))

    return jsonify(images)

@api.route("/api/v1/image", methods=["GET"])
def image():
    if not request.args.get('file_id'):
        return "Missing file_id parameter", 400

    image = File.objects(file_id=request.args.get('file_id')).first()

    if not image:
        return "Image does not exist", 400

    image.tags.sort(key=lambda x:x.tag.lower())
    tags = list(map(lambda x: API_Tag(tag=x.tag, category=x.category).__dict__, image.tags))
    image = API_File(file_id=image.file_id, folder_id=image.folder_id,
            name=image.name, tags=tags, description=image.description)
    
    return jsonify(image.__dict__)

@api.route("/api/v1/random_image", methods=["GET"])
def random_image():
    cursor = None
    tag = None
    print(request.args)

    if request.args.get('tag'):
        if request.args.get('exact') == 'True':
            tag = pymongo.db.tag.find_one({'tag': request.args.get('tag').strip()})
        else:
            tag = pymongo.db.tag.find_one({'tag': re.compile(request.args.get('tag').strip(), re.IGNORECASE)})
        
        if not tag:
            return "Tag '" + request.args.get('tag') + "' does not exist", 400

        cursor = pymongo.db.file.aggregate([
            { '$match': { 'tags': tag['_id'] } },
            { '$sample': { 'size': 1 } }
        ])
    else:
        cursor = pymongo.db.file.aggregate([
            { '$sample': { 'size': 1 } }
        ])

    result = list(cursor)
    if len(result) == 0:
        return "No images for " + tag['tag'], 400

    image = result[0]
    image['description'] = image['description'] if 'description' in image else None
    image['tags'] = list(pymongo.db.tag.find({ '_id': { '$in': image['tags'] }}))
    image['tag'] = tag['tag'] if tag else None

    image.pop('_id', None)
    for tag in image['tags']:
        tag.pop('_id', None)

    return jsonify(image)

@api.route("/api/v1/folder", methods=["GET"])
def folder():
    folder_id = request.args.get('folder_id')

    if not folder_id:
        return "Missing folder_id parameter", 400

    if folder_id == "root":
        folder_id = current_app.config['ROOT_ID']
    folder = Folder.objects(folder_id=folder_id).first()

    if not folder:
        return "Folder does not exist", 400

    children = list(Folder.objects(parent_id=folder.folder_id))
    children = list(map(lambda x: x.folder_id, children))

    files = list(File.objects(folder_id=folder.folder_id))
    files = list(map(lambda x: x.file_id, files))

    folder = API_Folder(folder_id=folder.folder_id, parent_id=folder.parent_id,
        files=files, children=children, name=folder.name, description=folder.description)
        

    return jsonify(folder.__dict__)

# routes for admins/root only below
@api.route("/api/v1/add_file_tags", methods=["POST"])
def add_file_tags():
    data = request.form
    
    if not 'username' in data: return "Username missing", 400
    username = data['username']
    if not 'api_key' in data: return "API key missing", 400
    api_key = data['api_key']
    
    user = User.objects(username=username).first()
    if user is None or user.api_key != api_key:
        return "Invalid credentials", 400
    if user.level >= 2: return "Insufficient permissions", 400
    
    if not 'file_id' in data: return "File id missing", 400
    file_id = data['file_id']
    
    image = File.objects(file_id=file_id).first()
    if image is None:
        return "Image does not exist", 400
    
    if not 'tags' in data: return "Tags missing", 400
    tags = dict(data.lists())['tags']
    tags = [x.strip() for x in tags]
    
    added = []
    not_added = []
    created = []

    for tag in tags:
        if tag != '':
            regex = re.compile("^" + tag + "$", re.IGNORECASE)
            existing_tag = Tag.objects(tag=regex).first()

            if existing_tag:
                if not any(x.tag.lower() == existing_tag.tag.lower() for x in image.tags):
                    image.tags.append(existing_tag)
                    added.append(tag)
                else:
                    not_added.append(tag)
            else:
                new_tag = Tag(tag=tag, category="Unsorted")
                new_tag.save()
                image.tags.append(new_tag)
                created.append(tag)

    image.save()

    return jsonify({'added':added,'not_added':not_added,'created':created})

@api.route("/api/v1/remove_file_tags", methods=["POST"])
def remove_file_tags():
    data = request.form
    
    if not 'username' in data: return "Username missing", 400
    username = data['username']
    if not 'api_key' in data: return "API key missing", 400
    api_key = data['api_key']
    
    user = User.objects(username=username).first()
    if user is None or user.api_key != api_key:
        return "Invalid credentials", 400
    if user.level >= 2: return "Insufficient permissions", 400
    
    if not 'file_id' in data: return "File id missing", 400
    file_id = data['file_id']
    
    image = File.objects(file_id=file_id).first()
    if image is None:
        return "Image does not exist", 400
    
    if not 'tags' in data: return "Tags missing", 400
    tags = dict(data.lists())['tags']
    
    removed = []
    not_removed = []

    for tag in tags:
        if tag.strip() != '':
            if any(x.tag.lower() == tag.lower() for x in image.tags):
                image.tags = list(filter(lambda x: x.tag.lower() != tag.lower(), image.tags))
                removed.append(tag)
            else:
                not_removed.append(tag)

    image.save()

    return jsonify({'removed':removed,'not_removed':not_removed})

@api.route("/api/v1/add_folder_tags", methods=["POST"])
def add_folder_tags():
    data = request.form
    
    if not 'username' in data: return "Username missing", 400
    username = data['username']
    if not 'api_key' in data: return "API key missing", 400
    api_key = data['api_key']
    
    user = User.objects(username=username).first()
    if user is None or user.api_key != api_key:
        return "Invalid credentials", 400
    if user.level >= 2: return "Insufficient permissions", 400
    
    if not 'folder_id' in data: return "Folder id missing", 400
    folder_id = current_app.config['ROOT_ID'] if data['folder_id'] == "root" else data['folder_id']

    folder = Folder.objects(folder_id=folder_id).first()
    if folder is None:
        return "Folder does not exist", 400
    files = list(File.objects(folder_id=folder.folder_id))
    
    if not 'tags' in data: return "Tags missing", 400
    tags = dict(data.lists())['tags']
    tags = [x.strip() for x in tags]
    
    images = []
    created = []

    add_tags = []
    for tag in tags:
        if tag != '':
            regex = re.compile("^" + tag + "$", re.IGNORECASE)
            existing_tag = Tag.objects(tag=regex).first()

            if not existing_tag:
                new_tag = Tag(tag=tag, category="Unsorted")
                new_tag.save()
                existing_tag = new_tag
                created.append(tag)

            add_tags.append(existing_tag)

    for image in files:
        added = []
        not_added = []

        for tag in add_tags:
            if not any(x.tag.lower() == tag.tag.lower() for x in image.tags):
                image.tags.append(tag)
                added.append(tag.tag)
            else:
                not_added.append(tag.tag)
        
        if len(added) > 0:
            image.save()
        images.append({'id':str(image.id),'added':added,'not_added':not_added})

    return jsonify({'images':images,'created':created})

@api.route("/api/v1/remove_folder_tags", methods=["POST"])
def remove_folder_tags():
    data = request.form
    
    if not 'username' in data: return "Username missing", 400
    username = data['username']
    if not 'api_key' in data: return "API key missing", 400
    api_key = data['api_key']
    
    user = User.objects(username=username).first()
    if user is None or user.api_key != api_key:
        return "Invalid credentials", 400
    if user.level >= 2: return "Insufficient permissions", 400
    
    if not 'folder_id' in data: return "Folder id missing", 400
    folder_id = current_app.config['ROOT_ID'] if data['folder_id'] == "root" else data['folder_id']
    
    folder = Folder.objects(folder_id=folder_id).first()
    if folder is None:
        return "Folder does not exist", 400
    files = list(File.objects(folder_id=folder.folder_id))
    
    if not 'tags' in data: return "Tags missing", 400
    tags = dict(data.lists())['tags']
    
    images = []

    for image in files:
        removed = []
        not_removed = []

        for tag in tags:
            if tag.strip() != '':
                if any(x.tag.lower() == tag.lower() for x in image.tags):
                    image.tags = list(filter(lambda x: x.tag.lower() != tag.lower(), image.tags))
                    removed.append(tag)
                else:
                    not_removed.append(tag)

        
        if len(removed) > 0:
            image.save()
        images.append({'id':str(image.id),'removed':removed,'not_removed':not_removed})

    return jsonify({'images':images})

@api.route("/api/v1/update_file_description", methods=["POST"])
def update_file_description():
    data = request.form
    
    if not 'username' in data: return "Username missing", 400
    username = data['username']
    if not 'api_key' in data: return "API key missing", 400
    api_key = data['api_key']
    
    user = User.objects(username=username).first()
    if user is None or user.api_key != api_key:
        return "Invalid credentials", 400
    if user.level >= 2: return "Insufficient permissions", 400
    
    if not 'file_id' in data: return "File id missing", 400
    file_id = data['file_id']
    
    image = File.objects(file_id=file_id).first()
    if image is None:
        return "Image does not exist", 400
    
    if not 'description' in data: return "Description missing", 400
    description = data['description'].strip()

    image.description = None if description == "" else description
    image.save()

    return jsonify()

@api.route("/api/v1/update_folder_description", methods=["POST"])
def update_folder_description():
    data = request.form
    
    if not 'username' in data: return "Username missing", 400
    username = data['username']
    if not 'api_key' in data: return "API key missing", 400
    api_key = data['api_key']
    
    user = User.objects(username=username).first()
    if user is None or user.api_key != api_key:
        return "Invalid credentials", 400
    if user.level >= 2: return "Insufficient permissions", 400
    
    if not 'folder_id' in data: return "Folder id missing", 400
    folder_id = data['folder_id']
    
    folder = Folder.objects(folder_id=folder_id).first()
    if folder is None:
        return "Folder does not exist", 400
    
    if not 'description' in data: return "Description missing", 400
    description = data['description'].strip()

    folder.description = None if description == "" else description
    folder.save()

    return jsonify()

@api.route("/api/v1/add_tags", methods=["POST"])
def add_tags():
    data = request.get_json()
    
    if not 'username' in data: return "Username missing", 400
    username = data['username']
    if not 'api_key' in data: return "API key missing", 400
    api_key = data['api_key']
    
    user = User.objects(username=username).first()
    if user is None or user.api_key != api_key:
        return "Invalid credentials", 400
    if user.level >= 2: return "Insufficient permissions", 400

    if not 'tags' in data: return "Tags missing", 400
    tags = data['tags']

    added = []
    not_added = []

    for t in tags:
        try:
            tag = t['tag'].strip()
            category = t['category'].strip()
        except:
            continue

        if tag and category:
            regex = re.compile("^" + tag + "$", re.IGNORECASE)
            existing_tag = Tag.objects(tag=regex).first()

            if existing_tag:
                not_added.append(tag)
            else:
                new_tag = Tag(tag=tag, category=category)
                new_tag.save()
                added.append(tag)
    
    return jsonify({'added':added,'not_added':not_added})

@api.route("/api/v1/remove_tags", methods=["POST"])
def remove_tags():
    data = request.get_json()
    
    if not 'username' in data: return "Username missing", 400
    username = data['username']
    if not 'api_key' in data: return "API key missing", 400
    api_key = data['api_key']
    
    user = User.objects(username=username).first()
    if user is None or user.api_key != api_key:
        return "Invalid credentials", 400
    if user.level >= 2: return "Insufficient permissions", 400

    if not 'tags' in data: return "Tags missing", 400
    tags = data['tags']

    removed = []
    not_removed = []

    for tag in tags:
        tag = tag.strip()

        if tag:
            regex = re.compile("^" + tag + "$", re.IGNORECASE)
            existing_tag = Tag.objects(tag=regex).first()

            if existing_tag:
                files = File.objects().filter(tags__contains=existing_tag.id)
                for image in files:
                    image.tags = list(filter(lambda x: x.tag.lower() != existing_tag.tag.lower(), image.tags))
                    image.save()

                existing_tag.delete()
                removed.append(tag)
            else:
                not_removed.append(tag)
    
    return jsonify({'removed':removed,'not_removed':not_removed})

@api.route("/api/v1/update_tags", methods=["POST"])
def update_tags():
    data = request.get_json()
    
    if not 'username' in data: return "Username missing", 400
    username = data['username']
    if not 'api_key' in data: return "API key missing", 400
    api_key = data['api_key']
    
    user = User.objects(username=username).first()
    if user is None or user.api_key != api_key:
        return "Invalid credentials", 400
    if user.level >= 2: return "Insufficient permissions", 400

    if not 'tags' in data: return "Tags missing", 400
    tags = data['tags']

    updated = []
    not_updated = []

    for t in tags:
        try:
            old_tag = t['old']['tag'].strip()
            old_category = t['old']['category'].strip()
            new_tag = t['new']['tag'].strip()
            new_category = t['new']['category'].strip()
        except:
            continue

        if old_tag and old_category and new_tag and new_category:
            regex = re.compile("^" + old_tag + "$", re.IGNORECASE)
            old_existing_tag = Tag.objects(tag=regex).first()
            regex = re.compile("^" + new_tag + "$", re.IGNORECASE)
            new_existing_tag = Tag.objects(tag=regex).first()

            if old_existing_tag and not new_existing_tag:
                old_existing_tag.tag = new_tag.strip()
                old_existing_tag.category = new_category.strip()
                old_existing_tag.save()
                updated.append(old_tag)
            else:
                not_updated.append(old_tag)
    
    return jsonify({'updated':updated,'not_updated':not_updated})