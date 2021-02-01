from flask import Blueprint, render_template, url_for, redirect, request, flash, current_app
from flask_login import current_user, login_required
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
        regex = re.compile(query, re.IGNORECASE)
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

    if addtagform.validate_on_submit() and current_user.is_authenticated:
        tag = addtagform.tag.data
        regex = re.compile(tag, re.IGNORECASE)

        if Tag.objects(tag=regex).first():
            flash("Tag '" + tag + "' already exists.", "narrow-warning")
        else:
            new_tag = Tag(tag=tag, category=addtagform.category.data)
            new_tag.save()
            flash("Tag '" + tag + "' added.", "narrow-success")

        return redirect(url_for("results.tags"))
    
    if deletetagform.validate_on_submit() and current_user.is_authenticated:
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

@results.route("/file/<file_id>", methods=["GET"])
def file(file_id):
    image = File.objects(file_id=file_id).first()
    folder = None
    if image:
        folder = Folder.objects(folder_id=image.folder_id).first()

    return render_template("image.html", title="Image", searchform=SearchForm(), image=image, folder=folder)

@results.route("/folder/<folder_id>", methods=["GET"])
def folder(folder_id):
    if folder_id == "root":
        folder_id = current_app.config['ROOT_ID']
    folder = Folder.objects(folder_id=folder_id).first()
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
        folder=folder, children=children, parent=parent, results=results_matrix)