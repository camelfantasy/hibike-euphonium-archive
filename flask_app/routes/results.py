from flask import Blueprint, render_template, url_for, redirect, flash, request, current_app
from flask_login import current_user
import re

from ..forms import SearchForm, AddTagForm, DeleteTagForm, UpdateDescriptionForm
from ..models import User, Tag, File, Folder, Metadata
from mongoengine.queryset.visitor import Q
from bson import ObjectId

results = Blueprint("results", __name__)

def getSearchTags():
	tags = list(map(lambda x: x.tag, Tag.objects()))
	tags.sort(key=lambda x:x.lower())
	return tags

# viewpoints below

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

@results.route("/api-documentation", methods=["GET"])
def api_documentation():
	metadata = Metadata(title="API Documentation")
	return render_template("api-documentation.html", title="API Documentation",
		searchform=SearchForm(), searchtags=getSearchTags(), metadata=metadata)

@results.route("/search-results/<query>", methods=["GET"])
def search_results(query):
	query = query.strip()
	files = []

	# use different logic for advanced search if below keywords are present
	if re.search(r'( AND | OR |NOT |\(|\))', query):
		files = advanced_search(query)
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
		searchtags=getSearchTags(), metadata=metadata, num_results=len(results))

@results.route("/all-images", methods=["GET"])
def all_images():
	files = File.objects()
	results = list(files)
	results.sort(key=lambda x:(x.folder_id, x.name.lower()))

	# arranges results into rows of 4 results each
	results_matrix = [results[i:i + 4] for i in range(0, len(results), 4)]

	# loads first 10 rows (40 images), stores any remaining files to be loaded dynamically
	initial_results = results_matrix[:10]
	remaining_results = list(map(lambda x: list(map(lambda y: y.file_id, x)),results_matrix[10:]))

	metadata = Metadata(title="All images",
		url=current_app.config["SITE_URL"] + url_for('results.all_images'),
		description="")
	return render_template("all_images.html", title="All images", searchform=SearchForm(),
		results=initial_results, remaining_results=remaining_results,
		searchtags=getSearchTags(), metadata=metadata, num_results=len(results))

@results.route("/untagged-images", methods=["GET"])
def untagged_images():
	files = File.objects(Q(tags__exists=False) | Q(tags__size=0))
	results = list(files)
	results.sort(key=lambda x:(x.folder_id, x.name.lower()))

	# arranges results into rows of 4 results each
	results_matrix = [results[i:i + 4] for i in range(0, len(results), 4)]

	# loads first 10 rows (40 images), stores any remaining files to be loaded dynamically
	initial_results = results_matrix[:10]
	remaining_results = list(map(lambda x: list(map(lambda y: y.file_id, x)),results_matrix[10:]))

	metadata = Metadata(title="Untagged images",
		url=current_app.config["SITE_URL"] + url_for('results.untagged_images'),
		description="")
	return render_template("untagged_images.html", title="Untagged images", searchform=SearchForm(),
		results=initial_results, remaining_results=remaining_results,
		searchtags=getSearchTags(), metadata=metadata, num_results=len(results))
		
@results.route("/tags", methods=["GET", "POST"])
def tags():
	addtagform = AddTagForm()
	deletetagform = DeleteTagForm()

	if request.form.get('submit_btn') == 'Add' and addtagform.validate_on_submit() \
		and current_user.is_authenticated and current_user.level < 2:
		tag = addtagform.tag.data.strip()

		# checks for empty tag
		if tag:
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
		else:
			flash("Tag cannot be empty.", "narrow-warning")

		return redirect(url_for("results.tags"))
	
	if request.form.get('submit_btn') == 'Delete' and deletetagform.validate_on_submit() \
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
	updatedescriptionform = UpdateDescriptionForm()
	image = File.objects(file_id=file_id).first()
	prev_id = None
	next_id = None

	folder = None
	if image:
		folder = Folder.objects(folder_id=image.folder_id).first()
		if image.tags:
			image.tags.sort(key=lambda x:x.tag.lower())

		files = list(File.objects(folder_id=folder.folder_id))
		files.sort(key=lambda x:x.name.lower())
		i = files.index(image)
		prev_id = None if i == 0 else files[i-1].file_id
		next_id = None if i == len(files) - 1 else files[i+1].file_id

	existing_tags = list(map(lambda x: x.tag, image.tags)) if image else []
	all_tags = list(map(lambda x: x.tag, Tag.objects()))
	all_tags.sort(key=lambda x:x.lower())
	suggestion_tags = list(filter(lambda x: x not in existing_tags, all_tags))

	title = "Image - " + image.name if image else "Error"
	updatedescriptionform.description.data = image.description if image else None
	metadata = Metadata(title=image.name if image else None,
		url=current_app.config["SITE_URL"] + url_for('results.file', file_id=file_id),
		description=", ".join(existing_tags) if len(existing_tags) <= 10
			else ", ".join(existing_tags[:10]) + "...",
		image='https://drive.google.com/thumbnail?id=' + image.file_id + '&sz=w1200' if image else None)
		
	return render_template("image.html", title=title, searchform=SearchForm(),
		addtagform=AddTagForm(), deletetagform=DeleteTagForm(), updatedescriptionform=updatedescriptionform,
		image=image, folder=folder, prev=prev_id, next=next_id, tags=suggestion_tags,
		searchtags=getSearchTags(), metadata=metadata)

@results.route("/folder/<folder_id>", methods=["GET", "POST"])
def folder(folder_id):
	updatedescriptionform = UpdateDescriptionForm()

	if folder_id == "root":
		folder_id = current_app.config['ROOT_ID']
	folder = Folder.objects(folder_id=folder_id).first()

	# gets assorted data associated with the folder
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

	add_tags = list(map(lambda x: x.tag, Tag.objects()))
	add_tags.sort(key=lambda x:x.lower())
	delete_tags = add_tags.copy()

	title = "Folder - " + folder.name if folder else "Error"
	updatedescriptionform.description.data = folder.description if folder else None
	metadata = Metadata(title=folder.name if folder else None,
		url=current_app.config["SITE_URL"] + url_for('results.folder',
		folder_id=folder_id), description="Folder")
	
	return render_template("folder.html", title=title, searchform=SearchForm(),
		addtagform=AddTagForm(), deletetagform=DeleteTagForm(), updatedescriptionform=updatedescriptionform,
		folder=folder, children=children, parent=parent, results=initial_results,
		remaining_results=remaining_results, add_tags=add_tags, delete_tags=delete_tags,
		searchtags=getSearchTags(), metadata=metadata, num_results=len(files))

# ajax routes below

@results.route("/add_file_tag", methods=["POST"])
def add_file_tag():
	success = -1
	message = ""
	
	tag = ""
	addtagform = AddTagForm()
	image = File.objects(file_id=addtagform.file_id.data).first() if addtagform.file_id is not None else None

	if addtagform.validate_on_submit() and current_user.is_authenticated and image:
		tag = addtagform.tag.data.strip()

		# checks for empty tag
		if tag:
			regex = re.compile("^" + tag + "$", re.IGNORECASE)
			existing_tag = Tag.objects(tag=regex).first()

			if existing_tag:
				if not any(x.tag.lower() == existing_tag.tag.lower() for x in image.tags):
					image.tags.append(existing_tag)
					message = "Tag '" + tag + "' added to image."
					success = 0
				else:
					message = "Tag '" + tag + "' already added."
					success = 1
			else:
				if current_user.level < 2:
					new_tag = Tag(tag=tag, category="Unsorted")
					new_tag.save()
					image.tags.append(new_tag)
					message = "Tag '" + tag + "' created and added to image."
					success = 2
				else:
					message = "New tag '" + tag + "' can only be added by an admin."
					success = 1
		else:
			message = "Tag cannot be empty."
			success = 1
		
		image.save()

	url = url_for('results.search_results', query=tag)
	
	return {'success':success, 'message':message, 'url_for':url, 'tag':tag}, 200

@results.route("/delete_file_tag", methods=["POST"])
def delete_file_tag():
	success = -1
	message = ""
	
	deletetagform = DeleteTagForm()
	image = File.objects(file_id=deletetagform.file_id.data).first() \
		if deletetagform.file_id is not None else None

	if deletetagform.validate_on_submit() and current_user.is_authenticated and image:
		tag = deletetagform.tag.data
		if any(x.tag.lower() == tag.lower() for x in image.tags):
			image.tags = list(filter(lambda x: x.tag.lower() != tag.lower(), image.tags))
			image.save()
			message = "Tag '" + tag + "' removed from image."
			success = 0
		
	return {'success':success, 'message':message}, 200

@results.route("/update_file_description", methods=["POST"])
def update_file_description():
	success = -1
	message = ""
	
	updatedescriptionform = UpdateDescriptionForm()
	image = File.objects(file_id=updatedescriptionform.file_id.data).first() \
		if updatedescriptionform.file_id is not None else None

	if updatedescriptionform.validate_on_submit() and current_user.is_authenticated and image:
		description = updatedescriptionform.description.data.strip()
		image.description = None if description == "" else description
		image.save()
		message = "Notes updated."
		success = 0

	return {'success':success, 'message':message}, 200

@results.route("/add_folder_tag", methods=["POST"])
def add_folder_tag():
	success = -1
	message = ""
	tag = ""

	addtagform = AddTagForm()
	folder_id = addtagform.file_id.data
	if folder_id == "root":
		folder_id = current_app.config['ROOT_ID']
	folder = Folder.objects(folder_id=folder_id).first()

	if addtagform.validate_on_submit() and current_user.is_authenticated and folder:
		files = list(File.objects(folder_id=folder.folder_id))
		tag = addtagform.tag.data.strip()
		existing_tag = None

		# checks for empty tag
		if tag:
			regex = re.compile("^" + tag + "$", re.IGNORECASE)
			existing_tag = Tag.objects(tag=regex).first()

			# add tag if it doesn't exist and sets messages first
			if not existing_tag:
				if current_user.level < 2:
					if len(files) != 0:
						new_tag = Tag(tag=tag, category="Unsorted")
						new_tag.save()
						existing_tag = new_tag
						message = "Tag '" + tag + "' created and added to {} images."
						success = 2
					else:
						message = "No images to update."
						success = 1
				else:
					message = "New tag '" + tag + "' can only be added by an admin."
					success = 1
			else:
				if len(files) != 0:
					message = "Tag '" + tag + "' added to {} images."
					success = 0
				else:
					message = "No images to update."
					success = 1
		else:
			message = "Tag cannot be empty."
			success = 1
		
		# checks against user with no permission to add a new tag
		if existing_tag:
			count = 0
			for image in files:
				if not any(x.tag.lower() == existing_tag.tag.lower() for x in image.tags):
					image.tags.append(existing_tag)
					image.save()
					count += 1

			message = message.format(count)

	return {'success':success, 'message':message, 'tag':tag}, 200

@results.route("/delete_folder_tag", methods=["POST"])
def delete_folder_tag():
	success = -1
	message = ""
	existing_tag = None

	deletetagform = DeleteTagForm()
	folder_id = deletetagform.file_id.data
	if folder_id == "root":
		folder_id = current_app.config['ROOT_ID']
	folder = Folder.objects(folder_id=folder_id).first()
	
	if deletetagform.validate_on_submit() and current_user.is_authenticated and folder:
		files = list(File.objects(folder_id=folder.folder_id))
		tag = deletetagform.tag.data
		regex = re.compile("^" + tag + "$", re.IGNORECASE)
		existing_tag = Tag.objects(tag=regex).first()

		if existing_tag:
			count = 0
			for image in files:
				if any(x.tag.lower() == tag.lower() for x in image.tags):
					image.tags = list(filter(lambda x: x.tag.lower() != tag.lower(), image.tags))
					image.save()
					count += 1
		
			if len(files) == 0:
				message = "No images to update."
				success = 1
			else:
				message = "Tag '" + tag + "' removed from " + str(count) + " images."
				success = 0
		else:
			message = "Tag '" + tag + "' does not exist."
			success = 1

	return {'success':success, 'message':message, 'tag':existing_tag.tag if existing_tag else None}, 200

@results.route("/update_folder_description", methods=["POST"])
def update_folder_description():
	success = -1
	message = ""

	updatedescriptionform = UpdateDescriptionForm()
	folder_id = updatedescriptionform.file_id.data
	if folder_id == "root":
		folder_id = current_app.config['ROOT_ID']
	folder = Folder.objects(folder_id=folder_id).first()

	if updatedescriptionform.validate_on_submit() and current_user.is_authenticated and folder:
		description = updatedescriptionform.description.data.strip()
		folder.description = None if description == "" else description
		folder.save()
		message = "Notes updated."
		success = 0

	return {'success':success, 'message':message}, 200

# advanced search functions below

db_query = [{"$unwind": "$tags"},
			{"$lookup":
				 {"from": "tag",
				  "localField": "tags",
				  "foreignField": "_id",
				  "as": "tags"
				  }
			 },
			{"$group": {
				"_id": "$_id",
				"tag": {"$first": "$tag"},
				"tags": {"$push": "$tags"}
			}
			}
			]

# handles advanced search flow
def advanced_search(query):
	try:
		tokens = lexer(query)
		tree = parse(tokens)
	except:
		return []

	ids = []
	files = list(File.objects.aggregate(*db_query)) + list(File.objects(Q(tags__exists=False) | Q(tags__size=0)))

	for f in files:
		if evaluate(tree, f["tags"]):
			# list has both dicts and objects
			try:
				ids.append(f["_id"])
			except:
				ids.append(f.id)

	return File.objects().filter(id__in=ids)

# lexes boolean expression
def lexer(expr):
	toks = []
	while len(expr) > 0:
		if re.search(r'^ ', expr):
			expr = expr[1:]
		elif re.search(r'^\(', expr):
			toks.append('L_PAREN')
			expr = expr[1:]
		elif re.search(r'^\)', expr):
			toks.append('R_PAREN')
			expr = expr[1:]
		elif re.search(r'^AND ', expr):
			toks.append('AND')
			expr = expr[4:]
		elif re.search(r'^OR ', expr):
			toks.append('OR')
			expr = expr[3:]
		elif re.search(r'^NOT ', expr):
			toks.append('NOT')
			expr = expr[4:]
		else:
			next_term = re.search(r'(AND|OR|NOT|\(|\))', expr)
			next_term_start = next_term.span()[0] if next_term else len(expr)
			term = re.search(r'\S+( +\S+)*', expr[:next_term_start])
			toks.append(term.group())
			expr = expr[len(term.group()):]

	return toks

# parses token list
def parse(toks):
	toks_left, tree = parse_helper(toks)
	if toks_left != []:
		raise Exception("Tokens left")
	else:
		return tree

def parse_helper(toks):
	return parse_OR(toks)

def parse_OR(toks):
	toks_left, tree1 = parse_AND(toks)
	if not toks_left:
		return toks_left, tree1
	else:
		if lookahead(toks_left) == "OR":
			toks_left = match(toks_left, "OR")
			toks_left, tree2 = parse_OR(toks_left)
			return toks_left, ('OR', tree1, tree2)
		else:
			return toks_left, tree1

def parse_AND(toks):
	toks_left, tree1 = parse_NOT(toks)
	if not toks_left:
		return toks_left, tree1
	else:
		if lookahead(toks_left) == "AND":
			toks_left = match(toks_left, "AND")
			toks_left, tree2 = parse_AND(toks_left)
			return toks_left, ('AND', tree1, tree2)
		else:
			return toks_left, tree1

def parse_NOT(toks):
	if lookahead(toks) == "NOT":
		toks_left = match(toks, "NOT")
		toks_left, tree1 = parse_NOT(toks_left)
		return toks_left, ('NOT', tree1)
	else:
		toks_left, tree1 = parse_PRIMARY(toks)
		return toks_left, tree1

def parse_PRIMARY(toks):
	if lookahead(toks) == "L_PAREN":
		toks_left = match(toks, "L_PAREN")
		toks_left, tree1 = parse_helper(toks_left)
		toks_left = match(toks_left, "R_PAREN")
		return toks_left, tree1
	elif re.search(r'^\S+( +\S+)*$', lookahead(toks)):
		tok = lookahead(toks)
		toks_left = match(toks, tok)
		return toks_left, ('ROLE', tok)
	else:
		raise Exception("Failure")

def lookahead(toks):
	if not toks:
		raise Exception("No tokens left")
	else:
		return toks[0]

def match(toks, tok):
	if not toks:
		raise Exception("No tokens left")
	elif toks[0] == tok:
		return toks[1:]
	else:
		raise Exception("Wrong token")

# evaluates tree with tag list
def evaluate(tree, tags):
	op = tree[0]
	if op == 'OR':
		return evaluate(tree[1], tags) or evaluate(tree[2], tags)
	elif op == 'AND':
		return evaluate(tree[1], tags) and evaluate(tree[2], tags)
	elif op == 'NOT':
		return not evaluate(tree[1], tags)
	else:
		return tree[1].lower() in [x[0]['tag'].lower() for x in tags]