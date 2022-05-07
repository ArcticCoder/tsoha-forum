from flask import session
from app import app
from db import db
from users import check_csrf
import threads


def get_all(thread_id):
    sql = "SELECT id, thread_id, user_id, message, TO_CHAR(time AT TIME ZONE 'UTC', "\
        "'YYYY-MM-DD HH24:MI:SS') as time, TO_CHAR(last_edit AT TIME ZONE 'UTC', "\
        "'YYYY-MM-DD HH24:MI:SS') as edit_time, "\
        "(SELECT COALESCE(SUM(amount), 0) FROM message_likes WHERE message_id = id) as likes "\
        "FROM messages WHERE thread_id=:thread_id ORDER BY time DESC, message;"
    return db.session.execute(sql, {"thread_id": thread_id}).fetchall()


def get_message(message_id):
    sql = "SELECT id, thread_id, user_id, message, TO_CHAR(time AT TIME ZONE 'UTC', "\
        "'YYYY-MM-DD HH24:MI:SS') as time, TO_CHAR(last_edit AT TIME ZONE 'UTC', "\
        "'YYYY-MM-DD HH24:MI:SS') as edit_time, "\
        "(SELECT COALESCE(SUM(amount), 0) FROM message_likes WHERE message_id = id) as likes "\
        "FROM messages WHERE id=:id;"
    return db.session.execute(sql, {"id": message_id}).fetchone()


def search(search_term: str):
    sql = "SELECT A.id, A.thread_id, A.user_id, A.message, TO_CHAR(A.time AT TIME ZONE 'UTC', "\
        "'YYYY-MM-DD HH24:MI:SS') as time, TO_CHAR(A.last_edit AT TIME ZONE 'UTC', "\
        "'YYYY-MM-DD HH24:MI:SS') as edit_time, "\
        "(SELECT COALESCE(SUM(amount), 0) FROM message_likes WHERE message_id = A.id) as likes "\
        "FROM messages A JOIN threads B ON A.thread_id=B.id "\
        "AND B.visible=true WHERE LOWER(message) LIKE LOWER(:search_term);"
    return db.session.execute(sql, {"search_term": "%"+search_term+"%"}).fetchall()


def visible(message_id):
    sql = "SELECT visible FROM messages WHERE id=:id;"
    result = db.session.execute(sql, {"id": message_id}).fetchone()
    if result:
        return result[0]
    return result


def create_message(thread_id, message):
    check_csrf()
    if not (threads.visible(thread_id) or session.get("is_admin")):
        return

    if session.get("user_id") and len(message) > 0 and len(message) <= 10000:
        try:
            sql = "INSERT INTO messages(thread_id, user_id, message) VALUES "\
                "(:thread_id, :user_id, :message);"
            db.session.execute(sql, {"thread_id": thread_id, "user_id": session.get(
                "user_id"), "message": message})
            db.session.commit()
        except:
            pass


def edit_message(message_id, new_message):
    check_csrf()
    message = get_message(message_id)
    if message:
        if (session.get("user_id") == message.user_id and
                len(new_message) > 0 and len(new_message) <= 10000):
            try:
                sql = "UPDATE messages SET message=:new_message, last_edit=CURRENT_TIMESTAMP "\
                    "WHERE id=:id;"
                db.session.execute(
                    sql, {"id": message_id, "new_message": new_message})
                db.session.commit()
            except:
                pass


def delete_message(message_id):
    check_csrf()
    message = get_message(message_id)
    if message:
        if session.get("is_admin") or session.get("user_id") == message.user_id:
            sql = "DELETE FROM messages WHERE id=:id;"
            db.session.execute(sql, {"id": message_id})
            db.session.commit()


@app.template_filter("check_message_vote")
def check_message_vote(message_id):
    sql = "SELECT amount FROM message_likes WHERE message_id=:id AND user_id=:user_id;"
    result = db.session.execute(
        sql, {"id": message_id, "user_id": session.get("user_id")}).fetchone()
    if result:
        return result[0]
    return result


def vote(message_id, amount: int):
    check_csrf()
    if check_message_vote(message_id):
        sql = "UPDATE message_likes SET amount=:amount "\
            "WHERE message_id=:message_id AND user_id=:user_id;"
    else:
        sql = "INSERT INTO message_likes(message_id, user_id, amount) "\
            "VALUES(:message_id, :user_id, :amount);"
    db.session.execute(
        sql, {"message_id": message_id, "user_id": session.get("user_id"), "amount": amount})
    db.session.commit()


def remove_vote(message_id):
    check_csrf()
    sql = "DELETE FROM message_likes WHERE message_id=:message_id AND user_id=:user_id;"
    db.session.execute(
        sql, {"message_id": message_id, "user_id": session.get("user_id")})
    db.session.commit()


def like_message(message_id):
    vote(message_id, 1)


def dislike_message(message_id):
    vote(message_id, -1)
