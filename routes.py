from app import app
from flask import redirect, render_template, request, session

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

        #TODO Implement username/password checking and DB lookups

        session["user_id"] = 0
        session["user_name"] = username
        return redirect("/")

#Logout "page"
@app.route("/logout")
def logout():
    del session["user_id"]
    del session["user_name"]
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

        #TODO Implement DB lookups, inserts and other account creation code

        if password == password_repeat:
            session["user_id"] = 0
            session["user_name"] = username
        return redirect("/")
