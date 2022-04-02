from db import db

def get_all_visible():
    sql = "SELECT A.id, A.topic FROM topics A WHERE A.visible=true ORDER BY A.topic"
    return db.session.execute(sql).fetchall()
