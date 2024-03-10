from sqlmodel import Session
from app.models import AndroidAppCreate, AndroidApp


def create_android_app(sess: Session, app: AndroidAppCreate):
    db_app = AndroidApp.model_validate(app)
    sess.add(db_app)
    sess.commit()
    sess.refresh(db_app)
    return db_app


def get_android_app(sess: Session, hash: str):
    return sess.get(AndroidApp, hash)


def update_android_app_ml_report(sess: Session, hash: str, ml_report: str):
    db_app = get_android_app(sess, hash)
    if db_app == None:
        return None
    db_app.ml_report = ml_report
    sess.add(db_app)
    sess.commit()
    sess.refresh(db_app)
    return db_app
