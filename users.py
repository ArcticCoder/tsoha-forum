from db import db
from flask import session

def login(username : str, password : str):
    #TODO Implement username/password checking and DB lookups
    session["user_id"] = 0
    session["user_name"] = username
    return True

def logout():
    del session["user_id"]
    del session["user_name"]

def username_available(username : str):
    return True

def register(username : str, password : str):
    #TODO Implement DB lookups, inserts and other account creation code
    login(username, password)
    return True
