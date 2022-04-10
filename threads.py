from db import db
from users import check_csrf
from flask import session

def get_all(id):
    if session.get("is_admin"):
        sql = "SELECT id, user_id, subject, visible FROM threads WHERE topic_id=:id ORDER BY visible DESC , subject;"
    else:
        sql = "SELECT id, user_id, subject, visible FROM threads WHERE topic_id=:id and (visible=true OR user_id=:user_id) ORDER BY subject;"
    return db.session.execute(sql, {"id":id, "user_id":session.get("user_id")}).fetchall()

def get_subject(id : int):
    sql = "SELECT subject FROM threads WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return result[0]
    return result

def available(subject):
    sql = "SELECT id FROM threads WHERE subject=:subject;"
    result = db.session.execute(sql, {"subject":subject})
    id = result.fetchone()
    return not id

def exists(id):
    sql = "SELECT id FROM threads WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return True
    return False

def visible(id):
    sql = "SELECT visible FROM threads WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return result[0]
    return result

#def create_subject(subject):
#    check_csrf()
#    if session.get("is_admin") and available(subject):
#        try:
#            sql = "INSERT INTO threads(subject) VALUES (:subject);"
#            db.session.execute(sql, {"subject":subject})
#            db.session.commit()
#        except:
#            pass
#
#def delete_subject(id : int):
#    check_csrf()
#    if session.get("is_admin"):
#        sql = "UPDATE threads SET visible =false WHERE id=:id;"
#        db.session.execute(sql, {"id":id})
#        db.session.commit()
#
#def restore_subject(id : int):
#    check_csrf()
#    if session.get("is_admin"):
#        sql = "UPDATE threads SET visible =true WHERE id=:id;"
#        db.session.execute(sql, {"id":id})
#        db.session.commit()
