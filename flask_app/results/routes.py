from flask import Blueprint, render_template, url_for, redirect, request, flash, current_app
from flask_login import current_user, login_required
import os, sqlite3
from sqlite3 import Error

from ..forms import SearchForm, AddTagForm, DeleteTagForm
from ..models import User, Tag

results = Blueprint("results", __name__)

@results.route("/", methods=["GET", "POST"])
def index():
    searchform = SearchForm()

    if searchform.validate_on_submit():
        return redirect(url_for("results.search_results", query=searchform.search_query.data))

    return render_template("index.html", searchform=searchform)

@results.route("/search-results/<query>", methods=["GET"])
def search_results(query):
    searchform=SearchForm()

    # code

    return render_template("search_results.html", title="Search - " + query, searchform=searchform, query=query)

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
            else:
                flash("Tag '" + tag + "' already exists.")
        except Error as e:
            flash("Server error.")
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
        except Error as e:
            flash("Server error.")
        finally:
            if conn:
                conn.close()
        return redirect(url_for("results.tags"))

    conn = None
    try:
        conn = sqlite3.connect(os.getcwd() + current_app.config['SQLITE_PATH'])
        c = conn.cursor()
        c.execute("SELECT tag, category from tags")
        result = c.fetchall()
    except Error as e:
        flash("Server error.")
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