from flask import abort, redirect, render_template, request, session
from app import app
import messages
import users
import threads
import topics


@app.after_request
def add_header(response):
    response.headers.add(
        "Cache-Control", "no-store, no-cache, must-revalidate, post-check=0, pre-check=0")
    return response

# Front page


@app.route("/")
def index():
    return render_template("index.html", topics=topics.get_all())

# Search


@app.route("/search", methods=["POST"])
def search():
    search_term = request.form["term"]
    if "thread_search" in request.form:
        return render_template("thread_search.html",
                               search_term=search_term, results=threads.search(search_term))
    if "message_search" in request.form:
        return render_template("message_search.html",
                               search_term=search_term, results=messages.search(search_term))
    return render_template("index.html", topics=topics.get_all(), message="Tunnistamaton virhe")

# ACCOUNTS
# Login


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        return render_template("login.html", message="Käyttäjänimi tai salasana väärin!")

# Logout "page"


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

# Account creation


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_repeat = request.form["password_repeat"]

        if not users.username_available(username):
            return render_template("register.html", message="Käyttäjänimi ei saatavilla!")

        if password_repeat != password:
            return render_template("register.html", message="Salasanat eivät täsmää!")

        if len(password) < 8:
            return render_template("register.html",
                                   message="Salasanan tulee olla vähintään 8 merkkiä pitkä!")

        if users.register(username, password):
            return redirect("/")

        return render_template("register.html",
                               message="Tunnistamaton virhe, yritä uudelleen tai ota yhteys "
                               "ylläpitäjään! (vili.sinerva@helsinki.fi)")

# TOPICS
# Open topic


@app.route("/topic/<int:topic_id>", methods=["GET"])
def topic(topic_id):
    if topics.exists(topic_id):
        if session.get("is_admin") or topics.visible(topic_id):
            return render_template("topic.html",
                                   topic=topics.get_topic(topic_id),
                                   threads=threads.get_all(topic_id))
        abort(401)
    abort(404)

# Topic creation


@app.route("/create_topic", methods=["POST"])
def create_topic():
    topic = request.form["topic"]
    if not topics.available(topic):
        return render_template("index.html",
                               topics=topics.get_all(), message="Alue on jo olemassa!")
    topics.create_topic(topic)
    return redirect("/")

# Topic deletion


@app.route("/delete_topic/<int:topic_id>", methods=["GET", "POST"])
def delete_topic(topic_id):
    if not session.get("is_admin"):
        abort(401)
    if request.method == "GET":
        return render_template("delete_topic.html", topic=topics.get_topic(topic_id))
    if request.method == "POST":
        topics.delete_topic(topic_id)
    return redirect("/")

# Topic restoration (un-deletion)


@app.route("/restore_topic/<int:topic_id>", methods=["POST"])
def restore_topic(topic_id):
    topics.restore_topic(topic_id)
    return redirect("/")

# THREADS


@app.route("/thread/<int:topic_id>", methods=["GET"])
def thread(topic_id):
    if threads.exists(topic_id):
        thread = threads.get_thread(topic_id)
        topic = topics.get_topic(thread.topic_id)
        if session.get("is_admin") or thread.visible or thread.user_id == session.get("user_id"):
            return render_template("thread.html",
                                   topic=topic, thread=thread, messages=messages.get_all(topic_id))
        abort(401)
    abort(404)

# Thread creation


@app.route("/create_thread/<int:topic_id>", methods=["GET", "POST"])
def create_thread(topic_id):
    if not session.get("user_id"):
        abort(401)
    if request.method == "GET":
        return render_template("create_thread.html", topic=topics.get_topic(topic_id))
    if request.method == "POST":
        thread = request.form["thread"]
        start_message = request.form["start_message"]

        if len(thread) < 1 or len(thread) > 100:
            return render_template("topic.html",
                                   threads=threads.get_all(topic_id),
                                   message="Otsikon pituus väärä!")
        if len(start_message) < 1 or len(start_message) > 10000:
            return render_template("topic.html",
                                   threads=threads.get_all(topic_id),
                                   message="Aloitusviestin pituus väärä!")

        new_id = threads.create_thread(topic_id, thread)
        if not new_id:
            return render_template("index.html",
                                   topics=topics.get_all(), message="Tunnistamaton virhe!")

        messages.create_message(new_id, start_message)

        return redirect(f"/thread/{new_id}")

# Thread deletion


@app.route("/delete_thread/<int:thread_id>", methods=["GET", "POST"])
def delete_thread(thread_id):
    thread = threads.get_thread(thread_id)
    if not (session.get("is_admin") or session.get("user_id") == thread.user_id):
        abort(401)
    if request.method == "GET":
        return render_template("delete_thread.html", thread=threads.get_thread(thread_id))
    if request.method == "POST":
        threads.delete_thread(thread_id)
    return redirect(f"/topic/{thread.topic_id}")

# Thread restoration (un-deletion)


@app.route("/restore_thread/<int:thread_id>", methods=["POST"])
def restore_thread(thread_id):
    threads.restore_thread(thread_id)
    thread = threads.get_thread(thread_id)
    if thread:
        return redirect(f"/thread/{thread_id}")
    return redirect("/")

# Like thread


@app.route("/like_thread", methods=["POST"])
def like_thread():
    thread_id = request.form["thread_id"]
    thread = threads.get_thread(thread_id)
    if thread:
        threads.like_thread(thread.id)
        return redirect(f"/topic/{thread.topic_id}")
    return redirect("/")

# Dislike thread


@app.route("/dislike_thread", methods=["POST"])
def dislike_thread():
    thread_id = request.form["thread_id"]
    thread = threads.get_thread(thread_id)
    if thread:
        threads.dislike_thread(thread.id)
        return redirect(f"/topic/{thread.topic_id}")
    return redirect("/")

# Remove vote from thread


@app.route("/remove_thread_vote", methods=["POST"])
def remove_thread_vote():
    thread_id = request.form["thread_id"]
    thread = threads.get_thread(thread_id)
    if thread:
        threads.remove_vote(thread.id)
        return redirect(f"/topic/{thread.topic_id}")
    return redirect("/")

# MESSAGES
# Creating messages


@app.route("/create_message/<int:thread_id>", methods=["POST"])
def create_message(thread_id):
    message = request.form["message"]
    if len(message) < 1 or len(message) > 10000:
        return render_template("thread.html",
                               thread=threads.get_thread(thread_id),
                               messages=messages.get_all(thread_id),
                               message="Viestin pituus väärä!")
    messages.create_message(thread_id, message)
    return redirect(f"/thread/{thread_id}")

# Editing message


@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    message = messages.get_message(message_id)
    if message:
        thread = threads.get_thread(message.thread_id)
        topic = topics.get_topic(thread.topic_id)
        if session.get("user_id") != message.user_id:
            abort(401)
        if request.method == "GET":
            return render_template("edit_message.html",
                                   topic=topic, thread=thread, edit_message=message)
        if request.method == "POST":
            new_message = request.form["new_message"]
            if new_message != message.message:
                messages.edit_message(message_id, new_message)
        return redirect(f"/thread/{thread.id}")


# Message deletion
@app.route("/delete_message/<int:message_id>", methods=["GET", "POST"])
def delete_message(message_id):
    message = messages.get_message(message_id)
    if not message:
        abort(404)
    if not (session.get("is_admin") or message.user_id == session.get("user_id")):
        abort(401)
    if request.method == "GET":
        return render_template("delete_message.html", deletable_message=message)
    if request.method == "POST":
        messages.delete_message(message_id)
    return redirect(f"/thread/{message.thread_id}")

# Like message


@app.route("/like_message", methods=["POST"])
def like_message():
    message_id = request.form["message_id"]
    message = messages.get_message(message_id)
    if message:
        messages.like_message(message.id)
        return redirect(f"/thread/{message.thread_id}")
    return redirect("/")

# Dislike message


@app.route("/dislike_message", methods=["POST"])
def dislike_message():
    message_id = request.form["message_id"]
    message = messages.get_message(message_id)
    if message:
        messages.dislike_message(message.id)
        return redirect(f"/thread/{message.thread_id}")
    return redirect("/")

# Remove vote from message


@app.route("/remove_message_vote", methods=["POST"])
def remove_message_vote():
    message_id = request.form["message_id"]
    message = messages.get_message(message_id)
    if message:
        messages.remove_vote(message.id)
        return redirect(f"/thread/{message.thread_id}")
    return redirect("/")

# MISSING PAGE


@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html", topics=topics.get_all(), message="Sivua ei löytynyt!")
