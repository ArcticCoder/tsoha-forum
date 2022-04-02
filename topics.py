from db import db
from flask import session

def get_all():
    if session.get("is_admin"):
        sql = "SELECT A.id, A.topic, A.visible FROM topics A ORDER BY A.visible DESC , A.topic;"
    else:
        sql = "SELECT A.id, A.topic, A.visible FROM topics A WHERE A.visible=true ORDER BY A.topic;"
    return db.session.execute(sql).fetchall()

def get_topic(id : int):
    sql = "SELECT topic FROM topics WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return result[0]
    return result

def available(topic):
    sql = "SELECT id FROM topics WHERE topic=:topic;"
    result = db.session.execute(sql, {"topic":topic})
    id = result.fetchone()
    return not id

def create_topic(topic):
    if session.get("is_admin") and available(topic):
        try:
            sql = "INSERT INTO topics(topic) VALUES (:topic);"
            db.session.execute(sql, {"topic":topic})
            db.session.commit()
        except:
            pass

def delete_topic(id : int):
    if session.get("is_admin"):
        sql = "UPDATE topics SET visible =false WHERE id=:id;"
        db.session.execute(sql, {"id":id})
        db.session.commit()

def restore_topic(id : int):
    if session.get("is_admin"):
        sql = "UPDATE topics SET visible =true WHERE id=:id;"
        db.session.execute(sql, {"id":id})
        db.session.commit()
