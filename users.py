from app import app
from db import db
import secrets
from flask import abort, request, session
from werkzeug.security import check_password_hash, generate_password_hash


def login(username: str, password: str):
    sql = "SELECT id, password_hash, is_admin FROM users WHERE username=:username;"
    result = db.session.execute(sql, {"username": username}).fetchone()
    if result:
        id, password_hash, admin = result
        if check_password_hash(password_hash, password):
            session["user_id"] = id
            session["user_name"] = username
            session["is_admin"] = admin
            session["csrf_token"] = secrets.token_hex(16)
            return True
    return False


def logout():
    del session["user_id"]
    del session["user_name"]
    del session["is_admin"]
    del session["csrf_token"]


def username_available(username: str):
    sql = "SELECT id FROM users WHERE username=:username;"
    result = db.session.execute(sql, {"username": username})
    id = result.fetchone()
    return not id


def register(username: str, password: str):
    if username_available(username) and len(password) >= 8:
        password_hash = generate_password_hash(password)
        try:
            sql = "INSERT INTO users(username, password_hash) VALUES (:username, :hash);"
            db.session.execute(
                sql, {"username": username, "hash": password_hash})
            db.session.commit()
        except:
            pass

    return login(username, password)


@app.template_filter("get_username")
def get_username(id):
    sql = "SELECT username FROM users WHERE id=:id;"
    result = db.session.execute(sql, {"id": id})
    name = result.fetchone()
    if name:
        return name[0]
    return name


def check_csrf():
    if session.get("csrf_token") != request.form["csrf_token"]:
        abort(401)
