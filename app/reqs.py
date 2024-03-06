import httpx
from pydantic import FilePath

from app.config import get_settings
from app.schemas.mobsf import (
    DownloadSourceResponse,
    ScanResponse,
    Error,
    UploadResponse,
)


async def mobsf_upload_file(file_name: str, file_data: bytes):
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            str(settings.mobsf_api_url) + "/upload",
            headers={"Authorization": settings.mobsf_secret},
            files={"file": (file_name, file_data)},
        )

    if resp.status_code != 200:
        raise Exception(Error.model_validate_json(resp.content).error)

    return UploadResponse.model_validate_json(resp.content).hash


async def mobsf_scan_file(hash: str):
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            str(settings.mobsf_api_url) + "/scan",
            headers={"Authorization": settings.mobsf_secret},
            data={"hash": hash},
            timeout=300,
        )

    if resp.status_code != 200:
        raise Exception(Error.model_validate_json(resp.content).error)

    return ScanResponse.model_validate_json(resp.content)


async def mobsf_download_source_file(hash: str, file: FilePath):
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            str(settings.mobsf_api_url) + "/view_source",
            headers={"Authorization": settings.mobsf_secret},
            data={"hash": hash, "file": file, "type": "apk"},
        )

    if resp.status_code != 200:
        raise Exception(Error.model_validate_json(resp.content).error)

    return DownloadSourceResponse.model_validate_json(resp.content)
