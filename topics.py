from db import db
import threads
from users import check_csrf
from flask import session

def get_all():
    if session.get("is_admin"):
        sql = "SELECT A.id, A.topic, A.visible, COUNT(B.id) as thread_count,  "\
                "COUNT(C.id) as message_count, TO_CHAR(MAX(C.time) AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as latest FROM "\
                "topics A LEFT JOIN threads B ON A.id=B.topic_id AND B.visible=true "\
                "LEFT JOIN messages C ON B.id=C.thread_id AND C.visible=true "\
                "GROUP BY A.id ORDER BY A.visible DESC , A.topic;"
    else:
        sql = "SELECT A.id, A.topic, A.visible, COUNT(B.id) as thread_count, "\
                "COUNT(C.id) as message_count, TO_CHAR(MAX(C.time) AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as latest FROM "\
                "topics A LEFT JOIN threads B ON A.id=B.topic_id AND A.visible=true AND B.visible=true "\
                "LEFT JOIN messages C ON B.id=C.thread_id AND C.visible=true "\
                "GROUP BY A.id ORDER BY A.visible DESC , A.topic;"
    return db.session.execute(sql).fetchall()

def get_topic(id : int):
    sql = "SELECT id, topic, visible FROM topics WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return result
    return result

def available(topic):
    sql = "SELECT id FROM topics WHERE topic=:topic;"
    result = db.session.execute(sql, {"topic":topic})
    id = result.fetchone()
    return not id

def exists(id):
    sql = "SELECT id FROM topics WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return True
    return False

def visible(id):
    sql = "SELECT visible FROM topics WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return result[0]
    return result

def create_topic(topic):
    check_csrf()
    if session.get("is_admin") and available(topic):
        try:
            sql = "INSERT INTO topics(topic) VALUES (:topic);"
            db.session.execute(sql, {"topic":topic})
            db.session.commit()
        except:
            pass

def delete_topic(id : int):
    check_csrf()
    if session.get("is_admin"):
        sql = "UPDATE topics SET visible =false WHERE id=:id;"
        db.session.execute(sql, {"id":id})
        db.session.commit()

def restore_topic(id : int):
    check_csrf()
    if session.get("is_admin"):
        sql = "UPDATE topics SET visible =true WHERE id=:id;"
        db.session.execute(sql, {"id":id})
        db.session.commit()
