import json
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, Response
from sqlmodel import Session
from app.config import Settings, get_settings
from app.db.curd import (
    create_android_app,
    get_android_app,
    list_android_apps,
    update_android_app,
)
from app.db.database import get_session
from app.depends import get_android_app_by_hash
from app.llm.chain import create_chain, llm_generate_report
from app.ml import get_xmal_model, ml_classify_malware
from xmalplus import XmalPlus
from app.db.models import AndroidApp, AndroidAppCreate, AndroidAppRead, AndroidAppUpdate

from app.reqs import (
    mobsf_download_file,
    mobsf_download_source_file,
    mobsf_upload_apk,
    mobsf_scan_apk,
)
from app.schemas.resp import StaticScanResult, MLScanResult, StaticScanResultSimple, TextFile


router = APIRouter(prefix="/api")


@router.post("/file", response_model=AndroidAppRead)
async def upload_apk_file(
    settings: Annotated[Settings, Depends(get_settings)],
    sess: Annotated[Session, Depends(get_session)],
    file: UploadFile,
):
    file_data = file.file.read()
    hash = await mobsf_upload_apk(
        settings.mobsf_url,
        settings.mobsf_secret,
        file.filename,
        file_data,
    )
    if get_android_app(sess, hash) != None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="apk already exist"
        )

    db_app = create_android_app(
        sess, AndroidAppCreate(hash=hash, name=file.filename, data=file_data)
    )
    return db_app


@router.get("/file", response_model=list[AndroidAppRead])
async def list_apk_files(sess: Annotated[Session, Depends(get_session)]):
    return list_android_apps(sess)


@router.get("/file/{hash}/icon")
async def get_icon(
    settings: Annotated[Settings, Depends(get_settings)],
    app: Annotated[AndroidApp, Depends(get_android_app_by_hash)],
):
    if app.icon_path == None:
        raise HTTPException(status_code=404, detail="icon not exist")

    file = await mobsf_download_file(settings.mobsf_url, app.icon_path)
    return Response(content=file, media_type="image/png")


@router.get("/file/{hash}/{file_path:path}", response_model=TextFile)
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


@router.get("/scan/static", response_model=StaticScanResult)
async def scan_apk_file(
    settings: Annotated[Settings, Depends(get_settings)],
    sess: Annotated[Session, Depends(get_session)],
    app: Annotated[AndroidApp, Depends(get_android_app_by_hash)],
):
    if app.static_result == None:
        mobsf_resp = await mobsf_scan_apk(
            settings.mobsf_url,
            settings.mobsf_secret,
            app.hash,
        )
        resp = StaticScanResult.from_mobsf(mobsf_resp)
        update_android_app(
            sess,
            app.hash,
            AndroidAppUpdate(
                static_result=resp.model_dump_json(),
                icon_path=mobsf_resp.icon_path,
            ),
        )
        return resp
    else:
        return StaticScanResult.model_validate_json(app.static_result)


@router.get("/scan/ml", response_model=MLScanResult)
async def scan_apk_file_ml(
    xmal_plus: Annotated[XmalPlus, Depends(get_xmal_model)],
    sess: Annotated[Session, Depends(get_session)],
    app: Annotated[AndroidApp, Depends(get_android_app_by_hash)],
):
    if app.ml_result == None:
        ml_result = await ml_classify_malware(xmal_plus, app.name, app.data)
        update_android_app(
            sess, app.hash, AndroidAppUpdate(ml_result=json.dumps(ml_result))
        )
        return ml_result
    else:
        return json.loads(app.ml_result)


@router.get("/report", response_model=TextFile)
async def generate_report(
    *,
    sess: Annotated[Session, Depends(get_session)],
    chain: Annotated[Any, Depends(create_chain)],
    app: Annotated[AndroidApp, Depends(get_android_app_by_hash)],
    regenerate: bool = False,
):
    if app.llm_report == None or regenerate:
        static_result = app.static_result if app.static_result != None else ""
        ml_result = app.ml_result if app.ml_result != None else ""
        report = await llm_generate_report(chain, StaticScanResultSimple.model_validate_json(static_result).model_dump(), ml_result)
        update_android_app(sess, app.hash, AndroidAppUpdate(llm_report=report))
        return TextFile(file="Report.md", data=report, type="md")
    else:
        return TextFile(file="Report.md", data=app.llm_report, type="md")
