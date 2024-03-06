from fastapi import APIRouter, HTTPException, UploadFile, Body, status

from app.reqs import mobsf_download_source_file, mobsf_upload_file, mobsf_scan_file
from app.schemas.file import File
from app.schemas.scan import ScanResponse

api = APIRouter(prefix="/api")


@api.post("/file")
async def upload_file(file: UploadFile):
    try:
        hash = await mobsf_upload_file(file.filename, file.file.read())
        return {"hash": hash}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.args
        )


@api.get("/scan")
async def scan_file(
    hash: str,
):
    try:
        mobsf_resp = await mobsf_scan_file(hash)
        resp = ScanResponse.from_mobsf(mobsf_resp)
        return resp
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.args
        )


@api.get("/source/{hash}/{file_path:path}", response_model=File)
async def view_source_file(hash: str, file_path: str):
    try:
        mobsf_resp = await mobsf_download_source_file(hash, file_path)
        return mobsf_resp
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.args
        )
