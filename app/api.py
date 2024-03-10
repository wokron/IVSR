import json
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlmodel import Session
from app.config import Settings, get_settings
from app.curd import (
    create_android_app,
    get_android_app,
    update_android_app,
    # update_android_app_llm_report,
    # update_android_app_ml_report,
    # update_android_app_static_report,
)
from app.database import get_session
from app.llm.chain import create_chain, generate_llm_report
from app.ml import get_xmal_model, ml_classify_malware
from xmalplus import XmalPlus
from app.models import AndroidAppCreate, AndroidAppUpdate

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
    sess: Annotated[Session, Depends(get_session)],
    hash: str,
):
    app = get_android_app(sess, hash)
    if app == None:
        raise HTTPException(
            status_code=404, detail="fail to find app with the given hash value"
        )
    if app.static_result == None:
        mobsf_resp = await mobsf_scan_file(
            settings.mobsf_url,
            settings.mobsf_secret,
            hash,
        )
        resp = ScanResult.from_mobsf(mobsf_resp)
        update_android_app(
            sess, hash, AndroidAppUpdate(static_result=resp.model_dump_json())
        )
        return resp
    else:
        return ScanResult.model_validate_json(app.static_result)


@api.get("/scan/learning")
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
    if app.ml_result == None:
        ml_result = await ml_classify_malware(xmal_plus, app.name, app.data)
        update_android_app(
            sess, hash, AndroidAppUpdate(ml_result=json.dumps(ml_result))
        )
        return ml_result
    else:
        return json.loads(app.ml_result)


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


@api.get("/report")
async def generate_report(
    *,
    sess: Annotated[Session, Depends(get_session)],
    chain: Annotated[Any, Depends(create_chain)],
    hash: str,
    regenerate: bool = False,
):
    app = get_android_app(sess, hash)
    if app == None:
        raise HTTPException(
            status_code=404, detail="fail to find app with the given hash value"
        )

    if app.llm_report == None or regenerate:
        report = await generate_llm_report(chain, app.static_result, app.ml_result)
        update_android_app(sess, hash, AndroidAppUpdate(llm_report=report))
        return {"report": report}
    else:
        return {"report": app.llm_report}
