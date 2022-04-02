from app import app
import users
from flask import redirect, render_template, request

#Front page
@app.route("/")
def index():
    return render_template("index.html")

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

        if password_repeat != password:
            return render_template("register.html", message="Salasanat eivät täsmää!")
        if not users.username_available(username):
            return render_template("register.html", message="Käyttäjänimi ei saatavilla!")

        if users.register(username, password):
            return redirect("/")

        return render_template("register.html", message="Tunnistamaton virhe, yritä uudelleen tai ota yhteys ylläpitäjään! (vili.sinerva@helsinki.fi)")
