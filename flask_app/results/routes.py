from flask import Blueprint, render_template, url_for, redirect, flash, request, current_app
from flask_login import current_user
import re

from ..forms import SearchForm, AddTagForm, DeleteTagForm
from ..models import User, Tag, File, Folder

results = Blueprint("results", __name__)

@results.route("/", methods=["GET", "POST"])
def index():
    searchform = SearchForm()

    if searchform.validate_on_submit():
        return redirect(url_for("results.search_results", query=searchform.search_query.data))

    return render_template("index.html", searchform=searchform)

@results.route("/about", methods=["GET"])
def about():
    return render_template("about.html", searchform=SearchForm())

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

    results = list(files)
    results.sort(key=lambda x:(x.folder_id, x.name.lower()))
    results_matrix = [results[i:i + 5] for i in range(0, len(results), 5)]

    title = ""
    if query.lower() == "all":
        title = "All images"
    elif query.lower() == "untagged":
        title = "Untagged images"
    else:
        title = "Search - " + query

    return render_template("search_results.html", title=title, searchform=SearchForm(), query=query, results=results_matrix)

@results.route("/tags", methods=["GET", "POST"])
def tags():
    addtagform = AddTagForm()
    deletetagform = DeleteTagForm()

    if request.form.get('submit') == 'Add' and addtagform.validate_on_submit() and current_user.is_authenticated:
        tag = addtagform.tag.data
        regex = re.compile("^" + tag + "$", re.IGNORECASE)

        if Tag.objects(tag=regex).first():
            flash("Tag '" + tag + "' already exists.", "narrow-warning")
        else:
            new_tag = Tag(tag=tag, category=addtagform.category.data)
            new_tag.save()
            flash("Tag '" + tag + "' added.", "narrow-success")

        return redirect(url_for("results.tags"))
    
    if request.form.get('submit') == 'Delete' and deletetagform.validate_on_submit() and current_user.is_authenticated:
        delete_tag = Tag.objects(tag=deletetagform.tag.data)
        delete_tag.delete()
        flash("Tag '" + deletetagform.tag.data + "' deleted.", "narrow-success")

        return redirect(url_for("results.tags"))

    result = list(Tag.objects())
    result.sort(key=lambda x:x.tag.lower())
        
    media = list(filter(lambda x: x.category == "Media", result))
    other = list(filter(lambda x: x.category == "Other", result))
    characters = list(filter(lambda x: x.category == "Characters", result))
    characters1 = characters[::2]
    characters2 = characters[1::2]
    
    return render_template("tags.html", title="Tags", searchform=SearchForm(),
        addtagform=addtagform, deletetagform=deletetagform, media=media, other=other,
        characters1=characters1, characters2=characters2)

@results.route("/file/<file_id>", methods=["GET", "POST"])
def file(file_id):
    addtagform = AddTagForm()
    deletetagform = DeleteTagForm()
    image = File.objects(file_id=file_id).first()

    if request.form.get('submit') == 'Add' and addtagform.validate_on_submit() and current_user.is_authenticated and image:
        tag = addtagform.tag.data
        regex = re.compile("^" + tag + "$", re.IGNORECASE)
        existing_tag = Tag.objects(tag=regex).first()

        if existing_tag:
            if not any(x.tag.lower() == existing_tag.tag.lower() for x in image.tags):
                image.tags.append(existing_tag)
        else:
            new_tag = Tag(tag=tag, category="Other")
            new_tag.save()
            image.tags.append(new_tag)
        
        image.save()
        return redirect(url_for("results.file", file_id=file_id))

    if request.form.get('submit') == 'Delete' and deletetagform.validate_on_submit() and current_user.is_authenticated and image:
        tag = deletetagform.tag.data
        if any(x.tag.lower() == tag.lower() for x in image.tags):
            image.tags = list(filter(lambda x: x.tag.lower() != tag.lower(), image.tags))
            image.save()
        
        return redirect(url_for("results.file", file_id=file_id))

    folder = None
    if image:
        folder = Folder.objects(folder_id=image.folder_id).first()
        if image.tags:
            image.tags.sort(key=lambda x:x.tag.lower())

    return render_template("image.html", title="Image", searchform=SearchForm(),
        addtagform=addtagform, deletetagform=deletetagform, image=image, folder=folder)

@results.route("/folder/<folder_id>", methods=["GET", "POST"])
def folder(folder_id):
    addtagform = AddTagForm()
    deletetagform = DeleteTagForm()

    if folder_id == "root":
        folder_id = current_app.config['ROOT_ID']
    folder = Folder.objects(folder_id=folder_id).first()


    if request.form.get('submit') == 'Add' and addtagform.validate_on_submit() and current_user.is_authenticated and folder:
        files = list(File.objects(folder_id=folder.folder_id))
        tag = addtagform.tag.data
        regex = re.compile("^" + tag + "$", re.IGNORECASE)
        existing_tag = Tag.objects(tag=regex).first()

        if not existing_tag:
            new_tag = Tag(tag=tag, category="Other")
            new_tag.save()
            existing_tag = new_tag
            
        for image in files:
            if not any(x.tag.lower() == existing_tag.tag.lower() for x in image.tags):
                image.tags.append(existing_tag)
                image.save()

        return redirect(url_for("results.folder", folder_id=folder_id))

    if request.form.get('submit') == 'Delete' and deletetagform.validate_on_submit() and current_user.is_authenticated and folder:
        files = list(File.objects(folder_id=folder.folder_id))
        tag = deletetagform.tag.data

        for image in files:
            if any(x.tag.lower() == tag.lower() for x in image.tags):
                image.tags = list(filter(lambda x: x.tag.lower() != tag.lower(), image.tags))
                image.save()
        
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

    results_matrix = [files[i:i + 5] for i in range(0, len(files), 5)]

    title = "Folder - " + folder.name if folder else "Folder"
    return render_template("folder.html", title=title, searchform=SearchForm(),
        addtagform=addtagform, deletetagform=deletetagform, folder=folder, children=children,
        parent=parent, results=results_matrix)