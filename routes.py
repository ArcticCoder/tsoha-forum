from app import app
import users
import threads
import topics
from flask import abort, redirect, render_template, request, session

#Front page
@app.route("/")
def index():
    return render_template("index.html", topics=topics.get_all())

#ACCOUNTS
#Login
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

#Logout "page"
@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

#Account creation
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
            return render_template("register.html", message="Salasanan tulee olla vähintään 8 merkkiä pitkä!")

        if users.register(username, password):
            return redirect("/")

        return render_template("register.html", message="Tunnistamaton virhe, yritä uudelleen tai ota yhteys ylläpitäjään! (vili.sinerva@helsinki.fi)")

#TOPICS
#Open topic
@app.route("/topic/<int:id>", methods=["GET"])
def topic(id):
    if topics.exists(id):
        if session.get("is_admin") or topics.visible(id):
            return render_template("topic.html", threads=threads.get_all(id))
        abort(401)
    abort(404)

#Topic creation
@app.route("/create_topic", methods=["POST"])
def create_topic():
    topic = request.form["topic"]
    if not topics.available(topic):
        return render_template("index.html", topics=topics.get_all(), message="Alue on jo olemassa!")
    topics.create_topic(topic)
    return redirect("/")

@app.route("/delete_topic/<int:id>", methods=["GET", "POST"])
def delete_topic(id):
    if(not session.get("is_admin")):
        abort(401)
    if request.method == "GET":
        return render_template("delete_topic.html", id=id, topic=topics.get_topic(id))
    if request.method == "POST":
        topics.delete_topic(id)
    return redirect("/")

@app.route("/restore_topic/<int:id>", methods=["POST"])
def restore_topic(id):
    topics.restore_topic(id)
    return redirect("/")

#THREADS

#MISSING PAGE
@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html", topics=topics.get_all(), message="Sivua ei löytynyt!")
