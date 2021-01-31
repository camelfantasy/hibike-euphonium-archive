from flask import Blueprint, render_template, url_for, redirect, request, flash, current_app
from flask_login import current_user, login_required
import os, sqlite3
from sqlite3 import Error

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
    db_result = []
    query = query.strip()

    try:
        conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
        c = conn.cursor()
        if query.lower() == "all":
            c.execute("SELECT file_id, name from file_ids")
        elif query.lower() == "untagged":
            c.execute("SELECT file_id, name from file_ids where tags=''")
        else:
            c.execute("SELECT file_id, name from file_ids where tags like ?", ["%" + query + "%"])
        db_result = c.fetchall()
    except Error as e:
        flash("Server error.", "warning")
    finally:
        if conn:
            conn.close()
    
    results = list(map(lambda x: File(x[0], None, x[1], None), db_result))
    results.sort(key=lambda x:x.name.lower())
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
        conn = None
        try:
            conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
            c = conn.cursor()

            tag = addtagform.tag.data.capitalize()
            c.execute("SELECT * from tags where tag=?", [tag])
            if c.fetchone() is None:
                c.execute("INSERT INTO tags(tag, category) values(?, ?)", (tag, addtagform.category.data))
                conn.commit()
                flash("Tag '" + tag + "' added.", "narrow-success")
            else:
                flash("Tag '" + tag + "' already exists.", "narrow-warning")
        except Error as e:
            flash("Server error.", "narrow-warning")
        finally:
            if conn:
                conn.close()
        return redirect(url_for("results.tags"))
    
    if deletetagform.validate_on_submit() and current_user.is_authenticated:
        conn = None
        try:
            conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
            c = conn.cursor()
            c.execute("DELETE FROM tags where tag=?", [deletetagform.tag.data])
            conn.commit()
            flash("Tag '" + deletetagform.tag.data + "' deleted.", "narrow-success")
        except Error as e:
            flash("Server error.", "wide-warning")
        finally:
            if conn:
                conn.close()
        return redirect(url_for("results.tags"))

    conn = None
    result = []
    
    try:
        conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
        c = conn.cursor()
        c.execute("SELECT tag, category from tags")
        result = c.fetchall()
    except Error as e:
        flash("Server error.", "wide-warning")
    finally:
        if conn:
            conn.close()

    tags = list(map(lambda x: Tag(x[0], x[1]), result))
    tags.sort(key=lambda x:x.tag.lower())
        
    media = list(filter(lambda x: x.category == "Media", tags))
    other = list(filter(lambda x: x.category == "Other", tags))
    characters = list(filter(lambda x: x.category == "Characters", tags))
    characters1 = characters[::2]
    characters2 = characters[1::2]
    
    return render_template("tags.html", title="Tags", searchform=SearchForm(),
        addtagform=addtagform, deletetagform=deletetagform, media=media, other=other,
        characters1=characters1, characters2=characters2)

@results.route("/file/<file_id>", methods=["GET"])
def file(file_id):
    conn = None
    image = None
    folder = None

    try:
        conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
        c = conn.cursor()
        c.execute("SELECT file_id, folder_id, name, tags from file_ids where file_id=?", [file_id])
        result = c.fetchone()
        if result:
            image = File(result[0], result[1], result[2], None if result[3] == "" else result[3].split(", "))
        
            c.execute("SELECT folder_id, name from folder_ids where folder_id=?", [image.folder_id])
            result = c.fetchone()
            if result:
                folder = Folder(result[0], result[1])
    except Error as e:
        flash("Server error.", "warning")
    finally:
        if conn:
            conn.close()

    return render_template("image.html", title="Image", searchform=SearchForm(), image=image, folder=folder)

@results.route("/folder/<folder_id>", methods=["GET"])
def folder(folder_id):
    conn = None
    folder = None
    parent = None

    try:
        conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
        c = conn.cursor()
        c.execute("SELECT folder_id, name from folder_ids where parent_id=?", [folder_id])
        result = c.fetchall()
        children = list(map(lambda x: Folder(x[0], x[1]), result))
        children.sort(key=lambda x:x.name.lower())

        c.execute("SELECT folder_id, parent_id, name from folder_ids where folder_id=?", [folder_id])
        result = c.fetchone()
        if result:
            folder = Folder(result[0], result[2])
            c.execute("SELECT folder_id, name from folder_ids where folder_id=?", [result[1]])
            result = c.fetchone()
            if result:
                parent = Folder(result[0], result[1])
    except Error as e:
        flash("Server error.", "warning")
    finally:
        if conn:
            conn.close()

    db_result = []
    try:
        conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
        c = conn.cursor()
        c.execute("SELECT file_id, name from file_ids where folder_id=?", [folder_id])
        db_result = c.fetchall()
    except Error as e:
        flash("Server error.", "warning")
    finally:
        if conn:
            conn.close()
    
    results = list(map(lambda x: File(x[0], None, x[1], None), db_result))
    results.sort(key=lambda x:x.name.lower())
    results_matrix = [results[i:i + 5] for i in range(0, len(results), 5)]

    title = "Folder - " + folder.name if folder else "Folder"
    return render_template("folder.html", title=title, searchform=SearchForm(),
        folder=folder, children=children, parent=parent, results=results_matrix)