from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile
from app.config import Settings, get_settings
from app.ml import get_xmal_model, ml_classify_malware
from xmalplus import XmalPlus

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
    file: UploadFile,
):
    hash = await mobsf_upload_apk(
        settings.mobsf_url,
        settings.mobsf_secret,
        file.filename,
        file.file.read(),
    )
    return {"hash": hash}


@api.get("/scan", response_model=ScanResult)
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


@api.post("/scan/ml")
async def scan_file_ml(
    xmal_plus: Annotated[XmalPlus, Depends(get_xmal_model)],
    file: UploadFile,
):
    result = await ml_classify_malware(xmal_plus, file.filename, file.file.read())
    return result
