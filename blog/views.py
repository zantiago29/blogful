from flask import render_template
from flask import request, redirect, url_for

from . import app
from .database import session, Entry

# Mistune - markdown parser for submitting formatted blog posts ##ask for clarification
import mistune

# Html2Text - convert html to markdown ##ask for clarification
import html2text

PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )
    
@app.route("/entry/add", methods=["GET"])
def add_entry_get():
    return render_template("add_entry.html")
    
@app.route("/entry/add", methods=["POST"])
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
# View single entry
@app.route("/entry/<int:id>")
def single_entry(id=1):
    entries = session.query(Entry)
    entries = entries.filter(Entry.id == id).all()
    return render_template("entries.html",
        entries=entries)
        
# GET request for editing existing entry
@app.route("/entry/<int:id>/edit", methods=["GET"])
def edit_entry_get(id=1):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id == id).first()
    return render_template("edit_entry.html", entry_title=entry.title, entry_content=html2text.html2text(entry.content))
        
# POST request for editing existing entry
@app.route("/entry/<int:id>/edit", methods=["POST"])
def edit_post_post(id=1):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id == id).first()
    entry.title=request.form["title"]
    entry.content=mistune.markdown(request.form["content"])
    session.commit()
    return redirect(url_for("entries"))

# GET request for deleting existing post
@app.route("/entry/<int:id>/delete", methods=["GET"])
def delete_entry_get(id=1):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id == id).first()
    return render_template("delete_entry.html", entry_title=entry.title)

# POST request for deleting existing post
@app.route("/entry/<int:id>/delete", methods=["POST"])
def delete_post_delete(id=1):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id == id).first()
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))      