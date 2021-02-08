from flask import Blueprint, render_template, url_for, redirect, flash, request, current_app
from flask_login import current_user
import re, json

from ..forms import SearchForm, AddTagForm, DeleteTagForm, UpdateDescriptionForm
from ..models import User, Tag, File, Folder, Metadata

results = Blueprint("results", __name__)

def getSearchTags():
    return list(map(lambda x: x.tag, Tag.objects()))

@results.route("/", methods=["GET", "POST"])
def index():
    searchform = SearchForm()

    if searchform.validate_on_submit():
        return redirect(url_for("results.search_results", query=searchform.search_query.data))

    all_users = list(User.objects())
    all_users.sort(key=lambda x:x.username.lower())
    users = list(filter(lambda x: x.level == 2, all_users))
    admins = list(filter(lambda x: x.level == 1, all_users))

    return render_template("index.html", searchform=searchform, users=users,
        admins=admins, searchtags=getSearchTags())

@results.route("/about", methods=["GET"])
def about():
    metadata = Metadata(title="About")
    return render_template("about.html", title="About", searchform=SearchForm(),
        searchtags=getSearchTags(), metadata=metadata)

@results.route("/search-results/<query>", methods=["GET"])
def search_results(query):
    conn = None
    query = query.strip()
    files = []

    if query.lower() == "all":
        files = File.objects()
    elif query.lower() == "untagged":
        files = File.objects(tags=[])
    else:
        regex = re.compile("^" + query + "$", re.IGNORECASE)
        tag = Tag.objects(tag=regex).first()
        if tag:
            files = File.objects().filter(tags__contains=tag.id)

        # saving below code for potential future use
        # regex will match for individual words in phrases but not substrings
        # regex = re.compile("^([a-z0-9 ]+ )?" + query + "( [a-z0-9 ]+)?$", re.IGNORECASE)
        # tags = Tag.objects(tag=regex)
        #
        # # multiple tags may be valid based on the query
        # for tag in tags:
        #     tag_files = File.objects().filter(tags__contains=tag.id)
        #     # ensure no duplication in returned results
        #     for tag_file in tag_files:
        #         if not any(x.file_id == tag_file.file_id for x in files):
        #             files.append(tag_file)

    results = list(files)
    results.sort(key=lambda x:(x.folder_id, x.name.lower()))

    # arranges results into rows of 4 results each
    results_matrix = [results[i:i + 4] for i in range(0, len(results), 4)]

    # loads first 10 rows (40 images), stores any remaining files to be loaded dynamically
    initial_results = results_matrix[:10]
    remaining_results = list(map(lambda x: list(map(lambda y: y.file_id, x)),results_matrix[10:]))

    title = ""
    if query.lower() == "all":
        title = "All images"
    elif query.lower() == "untagged":
        title = "Untagged images"
    else:
        title = "Search - " + query

    metadata = Metadata(title="Search results for: " + query,
        url=current_app.config["SITE_URL"] + url_for('results.search_results', query=query),
        description="")
    return render_template("search_results.html", title=title, searchform=SearchForm(),
        query=query, results=initial_results, remaining_results=remaining_results,
        searchtags=getSearchTags(), metadata=metadata)

@results.route("/tags", methods=["GET", "POST"])
def tags():
    addtagform = AddTagForm()
    deletetagform = DeleteTagForm()

    if request.form.get('submit') == 'Add' and addtagform.validate_on_submit() \
        and current_user.is_authenticated and current_user.level < 2:
        tag = addtagform.tag.data
        regex = re.compile("^" + tag + "$", re.IGNORECASE)

        existing_tag = Tag.objects(tag=regex).first()
        if existing_tag:
            if existing_tag.category == addtagform.category.data:
                flash("Tag '" + tag + "' already exists.", "narrow-warning")
            else:
                existing_tag.category = addtagform.category.data
                existing_tag.save()
                flash("Tag '" + tag + "' updated.", "narrow-success")
        else:
            new_tag = Tag(tag=tag, category=addtagform.category.data)
            new_tag.save()
            flash("Tag '" + tag + "' added.", "narrow-success")

        return redirect(url_for("results.tags"))
    
    if request.form.get('submit') == 'Delete' and deletetagform.validate_on_submit() \
        and current_user.is_authenticated and current_user.level < 2:
        delete_tag = Tag.objects(tag=deletetagform.tag.data).first()

        if delete_tag:
            files = File.objects().filter(tags__contains=delete_tag.id)
            for image in files:
                image.tags = list(filter(lambda x: x.tag.lower() != delete_tag.tag.lower(), image.tags))
                image.save()

            delete_tag.delete()
            flash("Tag '" + deletetagform.tag.data + "' deleted.", "narrow-success")

        return redirect(url_for("results.tags"))

    result = list(Tag.objects())
    result.sort(key=lambda x:x.tag.lower())
        
    media = list(filter(lambda x: x.category == "Media", result))
    other = list(filter(lambda x: x.category == "Other", result))
    unsorted = list(filter(lambda x: x.category == "Unsorted", result))
    characters = list(filter(lambda x: x.category == "Characters", result))

    # splits characters into three columns, going top-bottom then left-right
    mod = len(characters) % 3
    div = len(characters) // 3
    split1 = div if mod == 0 else div + 1
    split2 = 2*split1 if mod != 1 else 2*div+1

    characters1 = characters[:split1]
    characters2 = characters[split1:split2]
    characters3 = characters[split2:]
    
    metadata = Metadata(title="Tags", description="")
    return render_template("tags.html", title="Tags", searchform=SearchForm(),
        addtagform=addtagform, deletetagform=deletetagform, media=media, other=other,
        unsorted=unsorted, characters1=characters1, characters2=characters2,
        characters3=characters3, searchtags=getSearchTags(), metadata=metadata)

@results.route("/file/<file_id>", methods=["GET", "POST"])
def file(file_id):
    addtagform = AddTagForm()
    deletetagform = DeleteTagForm()
    updatedescriptionform = UpdateDescriptionForm()
    image = File.objects(file_id=file_id).first()

    if request.form.get('submit') == 'Add' and addtagform.validate_on_submit() \
        and current_user.is_authenticated and image:
        tag = addtagform.tag.data
        regex = re.compile("^" + tag + "$", re.IGNORECASE)
        existing_tag = Tag.objects(tag=regex).first()

        if existing_tag:
            if not any(x.tag.lower() == existing_tag.tag.lower() for x in image.tags):
                image.tags.append(existing_tag)
                flash("Tag '" + tag + "' added to image.", "success")
            else:
                flash("Tag '" + tag + "' already added.", "warning")
        else:
            if current_user.level < 2:
                new_tag = Tag(tag=tag, category="Unsorted")
                new_tag.save()
                image.tags.append(new_tag)
                flash("Tag '" + tag + "' created and added to image.", "success")
            else:
                flash("New tag '" + tag + "' can only be added by an admin.", "warning")
        
        image.save()
        return redirect(url_for("results.file", file_id=file_id))

    if request.form.get('submit') == 'Delete' and deletetagform.validate_on_submit() \
        and current_user.is_authenticated and image:
        tag = deletetagform.tag.data
        if any(x.tag.lower() == tag.lower() for x in image.tags):
            image.tags = list(filter(lambda x: x.tag.lower() != tag.lower(), image.tags))
            image.save()
            flash("Tag '" + tag + "' removed from image.", "success")
        
        return redirect(url_for("results.file", file_id=file_id))

    if request.form.get('submit') == 'Save' and updatedescriptionform.validate_on_submit() \
        and current_user.is_authenticated and image:
        description = updatedescriptionform.description.data.strip()
        image.description = None if description == "" else description
        image.save()
        flash("Notes updated.", "notes")
        return redirect(url_for("results.file", file_id=file_id))

    folder = None
    if image:
        folder = Folder.objects(folder_id=image.folder_id).first()
        if image.tags:
            image.tags.sort(key=lambda x:x.tag.lower())

    existing_tags = list(map(lambda x: x.tag, image.tags)) if image else []
    all_tags = list(map(lambda x: x.tag, Tag.objects()))
    suggestion_tags = list(filter(lambda x: x not in existing_tags, all_tags))

    title = "Image - " + image.name if image else "Error"
    updatedescriptionform.description.data = image.description if image else None
    image_type = image.name[image.name.rindex('.')+1:] if image and '.' in image.name else "jpeg"
    metadata = Metadata(title=image.name if image else None,
        url=current_app.config["SITE_URL"] + url_for('results.file', file_id=file_id),
        description=", ".join(existing_tags),
        image='https://drive.google.com/uc?id=' + image.file_id if image else None,
        image_type=image_type)
    return render_template("image.html", title=title, searchform=SearchForm(),
        addtagform=addtagform, deletetagform=deletetagform, updatedescriptionform=updatedescriptionform,
        image=image, folder=folder, tags=suggestion_tags, searchtags=getSearchTags(), metadata=metadata)

@results.route("/folder/<folder_id>", methods=["GET", "POST"])
def folder(folder_id):
    addtagform = AddTagForm()
    deletetagform = DeleteTagForm()
    updatedescriptionform = UpdateDescriptionForm()

    if folder_id == "root":
        folder_id = current_app.config['ROOT_ID']
    folder = Folder.objects(folder_id=folder_id).first()


    if request.form.get('submit') == 'Add' and addtagform.validate_on_submit() \
        and current_user.is_authenticated and folder:
        files = list(File.objects(folder_id=folder.folder_id))
        tag = addtagform.tag.data
        regex = re.compile("^" + tag + "$", re.IGNORECASE)
        existing_tag = Tag.objects(tag=regex).first()

        # add tag if it doesn't exist
        if not existing_tag:
            if current_user.level < 2:
                if len(files) != 0:
                    new_tag = Tag(tag=tag, category="Unsorted")
                    new_tag.save()
                    existing_tag = new_tag
                    flash("Tag '" + tag + "' created and added to images.", "success")
                else:
                    flash("No images to update.", "warning")
            else:
                flash("New tag '" + tag + "' can only be added by an admin.", "warning")
        else:
            if len(files) != 0:
                flash("Tag '" + tag + "' added to images.", "success")
            else:
                flash("No images to update.", "warning")
        
        # checks against user with no permission to add a new tag
        if existing_tag:
            for image in files:
                if not any(x.tag.lower() == existing_tag.tag.lower() for x in image.tags):
                    image.tags.append(existing_tag)
                    image.save()

        return redirect(url_for("results.folder", folder_id=folder_id))

    if request.form.get('submit') == 'Delete' and deletetagform.validate_on_submit() \
        and current_user.is_authenticated and folder:
        files = list(File.objects(folder_id=folder.folder_id))
        tag = deletetagform.tag.data
        regex = re.compile("^" + tag + "$", re.IGNORECASE)
        existing_tag = Tag.objects(tag=regex).first()

        if existing_tag:
            for image in files:
                if any(x.tag.lower() == tag.lower() for x in image.tags):
                    image.tags = list(filter(lambda x: x.tag.lower() != tag.lower(), image.tags))
                    image.save()
        
            if len(files) == 0:
                flash("No images to update.", "warning")
            else:
                flash("Tag '" + tag + "' removed from images.", "success")
        else:
            flash("Tag '" + tag + "' does not exist.", "warning")

        return redirect(url_for("results.folder", folder_id=folder_id))

    if request.form.get('submit') == 'Save' and updatedescriptionform.validate_on_submit() \
        and current_user.is_authenticated and folder:
        description = updatedescriptionform.description.data.strip()
        folder.description = None if description == "" else description
        folder.save()
        flash("Notes updated.", "notes")
        return redirect(url_for("results.folder", folder_id=folder_id))

    parent = None
    children = []
    files = []
    if folder:
        parent = Folder.objects(folder_id=folder.parent_id).first()
        children = list(Folder.objects(parent_id=folder.folder_id))
        children.sort(key=lambda x:x.name.lower())
        files = list(File.objects(folder_id=folder.folder_id))
        files.sort(key=lambda x:x.name.lower())

    # arranges results into rows of 4 results each
    results_matrix = [files[i:i + 4] for i in range(0, len(files), 4)]

    # loads first 10 rows (40 images), stores any remaining files to be loaded dynamically
    initial_results = results_matrix[:10]
    remaining_results = list(map(lambda x: list(map(lambda y: y.file_id, x)),results_matrix[10:]))

    tags = list(map(lambda x: x.tag, Tag.objects()))
    title = "Folder - " + folder.name if folder else "Error"
    updatedescriptionform.description.data = folder.description if folder else None
    metadata = Metadata(title=folder.name if folder else None,
        url=current_app.config["SITE_URL"] + url_for('results.folder',
        folder_id=folder_id), description="Folder")
    return render_template("folder.html", title=title, searchform=SearchForm(),
        addtagform=addtagform, deletetagform=deletetagform, updatedescriptionform=updatedescriptionform,
        folder=folder, children=children, parent=parent, results=initial_results,
        remaining_results=remaining_results, tags=tags, searchtags=getSearchTags(), metadata=metadata)