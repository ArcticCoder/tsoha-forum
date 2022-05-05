from app import app
from db import db
from users import check_csrf
from flask import session
import topics


def get_all(id):
    if session.get("is_admin"):
        sql = "SELECT A.id, A.topic_id, A.user_id, A.subject, A.visible, COUNT(B.id) as message_count, "\
              "TO_CHAR(MAX(B.time) AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as latest, "\
              "(SELECT COALESCE(SUM(amount), 0) FROM thread_likes WHERE thread_id=A.id) as likes "\
              "FROM threads A LEFT JOIN messages B ON A.id=B.thread_id "\
              "WHERE A.topic_id=:id "\
              "GROUP BY A.id ORDER BY A.visible DESC , latest DESC, A.subject;"
    else:
        sql = "SELECT A.id, A.topic_id, A.user_id, A.subject, A.visible, COUNT(B.id) as message_count, "\
              "TO_CHAR(MAX(B.time) AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as latest, "\
              "(SELECT COALESCE(SUM(amount), 0) FROM thread_likes WHERE thread_id=A.id) as likes "\
              "FROM threads A LEFT JOIN messages B ON A.id=B.thread_id "\
              "WHERE (A.visible=true OR A.user_id=:user_id) AND A.topic_id=:id "\
              "GROUP BY A.id ORDER BY A.visible DESC , latest DESC, A.subject;"
    return db.session.execute(sql, {"id": id, "user_id": session.get("user_id")}).fetchall()


def get_thread(id: int):
    sql = "SELECT id, topic_id, user_id, subject, visible FROM threads WHERE id=:id;"
    result = db.session.execute(sql, {"id": id}).fetchone()
    return result


def search(search_term: str):
    if session.get("is_admin"):
        sql = "SELECT A.id, A.topic_id, A.user_id, A.subject, A.visible, COUNT(B.id) as message_count, "\
              "TO_CHAR(MAX(B.time) AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as latest, "\
              "(SELECT COALESCE(SUM(amount), 0) FROM thread_likes WHERE thread_id=A.id) as likes "\
              "FROM threads A LEFT JOIN messages B ON A.id=B.thread_id "\
              "WHERE LOWER(A.subject) LIKE LOWER(:search_term) GROUP BY A.id ORDER BY A.visible DESC , latest DESC, A.subject;"
    else:
        sql = "SELECT A.id, A.topic_id, A.user_id, A.subject, A.visible, COUNT(B.id) as message_count, "\
              "TO_CHAR(MAX(B.time) AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as latest, "\
              "(SELECT COALESCE(SUM(amount), 0) FROM thread_likes WHERE thread_id=A.id) as likes "\
              "FROM threads A LEFT JOIN messages B ON A.id=B.thread_id "\
              "WHERE (A.visible=true OR A.user_id=:user_id) AND LOWER(A.subject) LIKE LOWER(:search_term) "\
              "GROUP BY A.id ORDER BY A.visible DESC , latest DESC, A.subject;"
    return db.session.execute(sql, {"user_id": session.get("user_id"), "search_term": "%"+search_term+"%"}).fetchall()


def exists(id):
    sql = "SELECT id FROM threads WHERE id=:id;"
    result = db.session.execute(sql, {"id": id}).fetchone()
    if result:
        return True
    return False


def visible(id):
    sql = "SELECT visible FROM threads WHERE id=:id;"
    result = db.session.execute(sql, {"id": id}).fetchone()
    if result:
        return result[0]
    return result


def create_thread(topic_id, subject):
    check_csrf()
    if not (topics.visible(topic_id) or session.get("is_admin")):
        return

    if session.get("user_id") and len(subject) > 0 and len(subject) <= 100:
        try:
            sql = "INSERT INTO threads(topic_id, user_id, subject) VALUES (:topic_id, :user_id, :subject) Returning threads.id;"
            new_id = db.session.execute(sql, {"topic_id": topic_id, "user_id": session.get(
                "user_id"), "subject": subject}).fetchone()
            db.session.commit()
            if new_id:
                return new_id[0]
            return
        except:
            pass


def delete_thread(id: int):
    check_csrf()
    thread = get_thread(id)
    if thread:
        if session.get("is_admin") or session.get("user_id") == thread.user_id:
            sql = "UPDATE threads SET visible =false WHERE id=:id;"
            db.session.execute(sql, {"id": id})
            db.session.commit()


def restore_thread(id: int):
    check_csrf()
    thread = get_thread(id)
    if thread:
        if session.get("is_admin") or session.get("user_id") == thread.user_id:
            sql = "UPDATE threads SET visible =true WHERE id=:id;"
            db.session.execute(sql, {"id": id})
            db.session.commit()


@app.template_filter("check_thread_vote")
def check_thread_vote(id: int):
    sql = "SELECT amount FROM thread_likes WHERE thread_id=:id AND user_id=:user_id;"
    result = db.session.execute(sql, {"id": id, "user_id": session.get("user_id")}).fetchone()
    if result:
        return result[0]
    return result


def vote(id: int, amount: int):
    check_csrf()
    thread = get_thread(id)
    if not thread.visible:
        return
    if check_thread_vote(id):
        sql = "UPDATE thread_likes SET amount=:amount WHERE thread_id=:thread_id AND user_id=:user_id;"
    else:
        sql = "INSERT INTO thread_likes(thread_id, user_id, amount) VALUES(:thread_id, :user_id, :amount);"
    db.session.execute(
        sql, {"thread_id": id, "user_id": session.get("user_id"), "amount": amount})
    db.session.commit()


def remove_vote(id: int):
    check_csrf()
    sql = "DELETE FROM thread_likes WHERE thread_id=:thread_id AND user_id=:user_id;"
    db.session.execute(
        sql, {"thread_id": id, "user_id": session.get("user_id")})
    db.session.commit()


def like_thread(id: int):
    vote(id, 1)


def dislike_thread(id: int):
    vote(id, -1)
