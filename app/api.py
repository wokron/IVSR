from fastapi import APIRouter, HTTPException, UploadFile, Body, status

from app.reqs import mobsf_download_source_file, mobsf_upload_file, mobsf_scan_file
from app.schemas.file import File
from app.schemas.scan import ScanResponse

api = APIRouter(prefix="/api")


@api.post("/file")
async def upload_file(file: UploadFile):
    hash = await mobsf_upload_file(file.filename, file.file.read())
    return {"hash": hash}


@api.get("/scan")
async def scan_file(
    hash: str,
):
    mobsf_resp = await mobsf_scan_file(hash)
    resp = ScanResponse.from_mobsf(mobsf_resp)
    return resp


@api.get("/source/{hash}/{file_path:path}", response_model=File)
async def view_source_file(hash: str, file_path: str):
    mobsf_resp = await mobsf_download_source_file(hash, file_path)
    return mobsf_resp
