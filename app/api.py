import json
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session
from app.config import Settings, get_settings
from app.curd import create_android_app, get_android_app, update_android_app_ml_report
from app.database import get_session
from app.ml import get_xmal_model, ml_classify_malware
from xmalplus import XmalPlus
from app.models import AndroidAppCreate

from app.reqs import (
    mobsf_download_source_file,
    mobsf_upload_apk,
    mobsf_scan_file,
)
from app.schemas.file import File, UploadResult
from app.schemas.scan import ScanResult

api = APIRouter(prefix="/api")


@api.post("/file", response_model=UploadResult)
async def upload_file(
    settings: Annotated[Settings, Depends(get_settings)],
    sess: Annotated[Session, Depends(get_session)],
    file: UploadFile,
):
    hash = await mobsf_upload_apk(
        settings.mobsf_url,
        settings.mobsf_secret,
        file.filename,
        file.file.read(),
    )
    create_android_app(
        sess, AndroidAppCreate(hash=hash, name=file.filename, data=file.file.read())
    )
    return {"hash": hash}


@api.get("/scan/static", response_model=ScanResult)
async def scan_file(
    settings: Annotated[Settings, Depends(get_settings)],
    hash: str,
):
    mobsf_resp = await mobsf_scan_file(
        settings.mobsf_url,
        settings.mobsf_secret,
        hash,
    )
    resp = ScanResult.from_mobsf(mobsf_resp)
    return resp


@api.post("/scan/learning")
async def scan_file_ml(
    xmal_plus: Annotated[XmalPlus, Depends(get_xmal_model)],
    sess: Annotated[Session, Depends(get_session)],
    hash: str,
):
    app = get_android_app(sess, hash)
    if app == None:
        raise HTTPException(
            status_code=404, detail="fail to find app with the given hash value"
        )
    result = await ml_classify_malware(xmal_plus, app.name, app.data)
    update_android_app_ml_report(sess, hash, json.dumps(result))
    return result


@api.get("/source/{hash}/{file_path:path}", response_model=File)
async def view_source_file(
    settings: Annotated[Settings, Depends(get_settings)],
    hash: str,
    file_path: str,
):
    mobsf_resp = await mobsf_download_source_file(
        settings.mobsf_url,
        settings.mobsf_secret,
        hash,
        file_path,
    )
    return mobsf_resp
