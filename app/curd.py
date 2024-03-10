from sqlmodel import Session
from app.models import AndroidAppCreate, AndroidApp, AndroidAppUpdate


def create_android_app(sess: Session, app: AndroidAppCreate):
    db_app = AndroidApp.model_validate(app)
    sess.add(db_app)
    sess.commit()
    sess.refresh(db_app)
    return db_app


def get_android_app(sess: Session, hash: str):
    return sess.get(AndroidApp, hash)


def update_android_app(sess: Session, hash: str, app: AndroidAppUpdate):
    db_app = get_android_app(sess, hash)
    if db_app == None:
        return None
    app_data = app.model_dump(exclude_unset=True)
    db_app.sqlmodel_update(app_data)
    sess.add(db_app)
    sess.commit()
    sess.refresh(db_app)
    return db_app
