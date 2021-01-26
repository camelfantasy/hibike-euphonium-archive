from flask import Blueprint, render_template, url_for, redirect, request, flash, current_app
from flask_login import current_user

from ..forms import SearchForm
from ..models import User

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

    # code
    
    return render_template("tags.html", title="Tags", searchform=SearchForm())