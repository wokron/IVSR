from sqlmodel import SQLModel, Session, create_engine

from app.db import models
from app.db.curd import create_android_app, get_android_app, update_android_app


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
            "icon_path": None,
            "static_result": None,
            "ml_result": None,
            "llm_report": None,
        }

        app2 = get_android_app(sess, "1234")
        assert app1.model_dump() == app2.model_dump()

        app3 = update_android_app(
            sess, "1234", models.AndroidAppUpdate(ml_result="this is report")
        )
        assert app3.ml_result != None
