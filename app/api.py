import json
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, Response
from sqlmodel import Session
from app.config import Settings, get_settings
from app.curd import (
    create_android_app,
    get_android_app,
    list_android_apps,
    update_android_app,
)
from app.database import get_session
from app.llm.chain import create_chain, llm_generate_report
from app.ml import get_xmal_model, ml_classify_malware
from xmalplus import XmalPlus
from app.models import AndroidAppCreate, AndroidAppRead, AndroidAppUpdate

from app.reqs import (
    mobsf_download_file,
    mobsf_download_source_file,
    mobsf_upload_apk,
    mobsf_scan_apk,
)
from app.schemas.resp import StaticScanResult, MLScanResult, SourceFile


router = APIRouter(prefix="/api")


@router.post("/apk", response_model=AndroidAppRead)
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


@router.get("/apk", response_model=list[AndroidAppRead])
async def list_apk_files(sess: Annotated[Session, Depends(get_session)]):
    return list_android_apps(sess)


@router.get("/scan/static", response_model=StaticScanResult)
async def scan_apk_file(
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
        mobsf_resp = await mobsf_scan_apk(
            settings.mobsf_url,
            settings.mobsf_secret,
            hash,
        )
        resp = StaticScanResult.from_mobsf(mobsf_resp)
        update_android_app(
            sess,
            hash,
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


@router.get("/apk/{hash}/icon")
async def get_icon(
    settings: Annotated[Settings, Depends(get_settings)],
    sess: Annotated[Session, Depends(get_session)],
    hash: str,
):
    app = get_android_app(sess, hash)
    if app == None:
        raise HTTPException(
            status_code=404, detail="fail to find app with the given hash value"
        )
    if app.icon_path == None:
        raise HTTPException(status_code=404, detail="icon not exist")

    file = await mobsf_download_file(settings.mobsf_url, app.icon_path)
    return Response(content=file, media_type="image/png")


@router.get("/apk/{hash}/{file_path:path}", response_model=SourceFile)
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


@router.get("/report")
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
        static_result = app.static_result if app.static_result != None else ""
        ml_result = app.ml_result if app.ml_result != None else ""
        report = await llm_generate_report(chain, json.loads(static_result), ml_result)
        update_android_app(sess, hash, AndroidAppUpdate(llm_report=report))
        return {"report": report}
    else:
        return {"report": app.llm_report}
