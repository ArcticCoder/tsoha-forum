from db import db
from users import check_csrf
from flask import session
import threads

def get_all(id):
    sql = "SELECT id, thread_id, user_id, message, TO_CHAR(time AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as time, "\
            "TO_CHAR(last_edit AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as edit_time FROM messages WHERE thread_id=:thread_id ORDER BY time DESC, message;"
    return db.session.execute(sql, {"thread_id":id}).fetchall()

def get_message(id):
    sql = "SELECT id, thread_id, user_id, message, TO_CHAR(time AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as time, "\
            "TO_CHAR(last_edit AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') as edit_time FROM messages WHERE id=:id;"
    return db.session.execute(sql, {"id":id}).fetchone()

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
