from flask import session
from db import db
from users import check_csrf


def get_all():
    if session.get("is_admin"):
        sql = "SELECT A.id, A.topic, A.visible, COUNT(DISTINCT B.id) as thread_count,  "\
            "COUNT(C.id) as message_count, TO_CHAR(MAX(C.time) AT TIME ZONE 'UTC', "\
            "'YYYY-MM-DD HH24:MI:SS') as latest FROM "\
            "topics A LEFT JOIN threads B ON A.id=B.topic_id AND B.visible=true "\
            "LEFT JOIN messages C ON B.id=C.thread_id "\
            "GROUP BY A.id ORDER BY A.visible DESC , A.topic;"
    else:
        sql = "SELECT A.id, A.topic, A.visible, COUNT(DISTINCT B.id) as thread_count,  "\
            "COUNT(C.id) as message_count, TO_CHAR(MAX(C.time) AT TIME ZONE 'UTC', "\
            "'YYYY-MM-DD HH24:MI:SS') as latest FROM "\
            "topics A LEFT JOIN threads B ON A.id=B.topic_id AND B.visible=true "\
            "LEFT JOIN messages C ON B.id=C.thread_id WHERE A.visible=true "\
            "GROUP BY A.id ORDER BY A.visible DESC , A.topic;"
    return db.session.execute(sql).fetchall()


def get_topic(topic_id):
    sql = "SELECT id, topic, visible FROM topics WHERE id=:id;"
    result = db.session.execute(sql, {"id": topic_id}).fetchone()
    if result:
        return result
    return result


def available(topic):
    sql = "SELECT id FROM topics WHERE topic=:topic;"
    result = db.session.execute(sql, {"topic": topic})
    topic_id = result.fetchone()
    return not topic_id


def exists(topic_id):
    sql = "SELECT id FROM topics WHERE id=:id;"
    result = db.session.execute(sql, {"id": topic_id}).fetchone()
    if result:
        return True
    return False


def visible(topic_id):
    sql = "SELECT visible FROM topics WHERE id=:id;"
    result = db.session.execute(sql, {"id": topic_id}).fetchone()
    if result:
        return result[0]
    return result


def create_topic(topic):
    check_csrf()
    if session.get("is_admin") and available(topic):
        try:
            sql = "INSERT INTO topics(topic) VALUES (:topic);"
            db.session.execute(sql, {"topic": topic})
            db.session.commit()
        except:
            pass


def delete_topic(topic_id):
    check_csrf()
    if session.get("is_admin"):
        sql = "UPDATE topics SET visible =false WHERE id=:id;"
        db.session.execute(sql, {"id": topic_id})
        db.session.commit()


def restore_topic(topic_id):
    check_csrf()
    if session.get("is_admin"):
        sql = "UPDATE topics SET visible =true WHERE id=:id;"
        db.session.execute(sql, {"id": topic_id})
        db.session.commit()
