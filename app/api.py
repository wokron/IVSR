from fastapi import APIRouter, UploadFile

from app.reqs import mobsf_download_source_file, mobsf_upload_apk, mobsf_scan_file
from app.schemas.file import File, UploadResult
from app.schemas.scan import ScanResult

api = APIRouter(prefix="/api")


@api.post("/file", response_model=UploadResult)
async def upload_file(file: UploadFile):
    hash = await mobsf_upload_apk(file.filename, file.file.read())
    return {"hash": hash}


@api.get("/scan", response_model=ScanResult)
async def scan_file(
    hash: str,
):
    mobsf_resp = await mobsf_scan_file(hash)
    resp = ScanResult.from_mobsf(mobsf_resp)
    return resp


@api.get("/source/{hash}/{file_path:path}", response_model=File)
async def view_source_file(hash: str, file_path: str):
    mobsf_resp = await mobsf_download_source_file(hash, file_path)
    return mobsf_resp
