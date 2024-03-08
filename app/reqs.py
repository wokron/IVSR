import httpx
from pydantic import FilePath
from fastapi import HTTPException

from app.config import get_settings
from app.schemas.mobsf import (
    DownloadSourceResponse,
    ScanResponse,
    Error,
    UploadResponse,
)


async def mobsf_upload_apk(file_name: str, file_data: bytes):
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            str(settings.mobsf_url) + "api/v1/upload",
            headers={"Authorization": settings.mobsf_secret},
            files={"file": (file_name, file_data)},
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=Error.model_validate_json(resp.content).error,
        )

    return UploadResponse.model_validate_json(resp.content).hash


async def mobsf_download_apk(hash: str):
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.get(str(settings.mobsf_url) + f"download/{hash}.apk")

    return resp.read()


async def mobsf_scan_file(hash: str):
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            str(settings.mobsf_url) + "api/v1/scan",
            headers={"Authorization": settings.mobsf_secret},
            data={"hash": hash},
            timeout=300,
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=Error.model_validate_json(resp.content).error,
        )

    return ScanResponse.model_validate_json(resp.content)


async def mobsf_download_source_file(hash: str, file: FilePath):
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            str(settings.mobsf_url) + "api/v1/view_source",
            headers={"Authorization": settings.mobsf_secret},
            data={"hash": hash, "file": file, "type": "apk"},
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=Error.model_validate_json(resp.content).error,
        )

    return DownloadSourceResponse.model_validate_json(resp.content)
