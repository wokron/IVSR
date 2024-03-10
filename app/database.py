from sqlmodel import SQLModel, Session, create_engine

from app.config import get_settings
from app import models  # don't move this


engine = create_engine(str(get_settings().sqlite_url))


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
