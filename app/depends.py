from typing import Annotated
from fastapi import Depends, HTTPException, status

from sqlmodel import Session
from app.db.curd import get_android_app

from app.db.database import get_session


def get_android_app_by_hash(
    sess: Annotated[Session, Depends(get_session)],
    hash: str,
):
    app = get_android_app(sess, hash)
    if app == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="fail to find app with the given hash value",
        )
    return app
