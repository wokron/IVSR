from sqlmodel import SQLModel, Session, create_engine

from app import models
from app.curd import create_android_app, get_android_app, update_android_app_ml_report


def test_android_app_curd():
    engine = create_engine(
        "sqlite:///testing.db", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as sess:
        app1 = create_android_app(
            sess,
            models.AndroidAppCreate(
                hash="1234", name="Android App1", data=bytes("some data", "utf-8")
            ),
        )
        assert app1.model_dump() == {
            "hash": "1234",
            "name": "Android App1",
            "data": bytes("some data", "utf-8"),
            "ml_report": None,
        }

        app2 = get_android_app(sess, "1234")
        assert app1.model_dump() == app2.model_dump()

        app3 = update_android_app_ml_report(sess, "1234", "this is report")
        assert app3.ml_report != None
