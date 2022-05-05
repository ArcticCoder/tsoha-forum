from app import app
from db import db
from users import check_csrf
from flask import session
import threads

def get_all(id):
    sql = "SELECT A.id, A.thread_id, A.user_id, A.message, TO_CHAR(A.time AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as time, "\
            "TO_CHAR(A.last_edit AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as edit_time, COALESCE(SUM(B.amount), 0) as likes "\
            "FROM messages A LEFT JOIN message_likes B ON A.id=B.message_id WHERE A.thread_id=:thread_id "\
            "GROUP BY A.id ORDER BY A.time DESC, A.message;"
    return db.session.execute(sql, {"thread_id":id}).fetchall()

def get_message(id):
    sql = "SELECT A.id, A.thread_id, A.user_id, A.message, TO_CHAR(A.time AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as time, "\
            "TO_CHAR(A.last_edit AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as edit_time, COALESCE(SUM(B.amount), 0) as likes "\
            "FROM messages A LEFT JOIN message_likes B ON A.id=B.message_id WHERE A.id=:id GROUP BY A.id;"
    return db.session.execute(sql, {"id":id}).fetchone()

def search(search_term : str):
    sql = "SELECT A.id, A.thread_id, A.user_id, A.message, TO_CHAR(A.time AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as time, "\
            "TO_CHAR(A.last_edit AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as edit_time FROM messages A JOIN threads B ON A.thread_id=B.id "\
            "AND B.visible=true WHERE LOWER(message) LIKE LOWER(:search_term);"
    return db.session.execute(sql, {"search_term":"%"+search_term+"%"}).fetchall()

def visible(id):
    sql = "SELECT visible FROM messages WHERE id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return result[0]
    return result

def create_message(thread_id, message):
    check_csrf()
    if not (threads.visible(thread_id) or session.get("is_admin")):
        return

    if session.get("user_id") and len(message) > 0 and len(message) <= 10000:
        try:
            sql = "INSERT INTO messages(thread_id, user_id, message) VALUES (:thread_id, :user_id, :message);"
            db.session.execute(sql, {"thread_id":thread_id, "user_id":session.get("user_id"), "message":message})
            db.session.commit()
        except:
            pass

def edit_message(id, new_message):
    check_csrf()
    message = get_message(id)
    if message:
        if session.get("user_id") == message.user_id and len(new_message) > 0 and len(new_message) <= 10000:
            try:
                sql = "UPDATE messages SET message=:new_message, last_edit=CURRENT_TIMESTAMP WHERE id=:id;"
                db.session.execute(sql, {"id":id, "new_message":new_message})
                db.session.commit()
            except:
                pass

def delete_message(id : int):
    check_csrf()
    message = get_message(id)
    if message:
        if session.get("is_admin") or session.get("user_id") == message.user_id:
            sql = "DELETE FROM messages WHERE id=:id;"
            db.session.execute(sql, {"id":id})
            db.session.commit()

@app.template_filter("check_message_vote")
def check_message_vote(id : int):
    sql = "SELECT amount FROM message_likes WHERE message_id=:id;"
    result = db.session.execute(sql, {"id":id}).fetchone()
    if result:
        return result[0]
    return result

def vote(id : int, amount : int):
    check_csrf()
    message = get_message(id)
    if check_message_vote(id):
        sql = "UPDATE message_likes SET amount=:amount WHERE message_id=:message_id AND user_id=:user_id;"
    else:
        sql = "INSERT INTO message_likes(message_id, user_id, amount) VALUES(:message_id, :user_id, :amount);"
    db.session.execute(sql, {"message_id":id, "user_id":session.get("user_id"), "amount":amount})
    db.session.commit()

def remove_vote(id : int):
    check_csrf()
    sql = "DELETE FROM message_likes WHERE message_id=:message_id AND user_id=:user_id;"
    db.session.execute(sql, {"message_id":id, "user_id":session.get("user_id")})
    db.session.commit()

def like_message(id : int):
    vote(id, 1)

def dislike_message(id : int):
    vote(id, -1)
