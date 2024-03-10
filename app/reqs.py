import httpx
from pydantic import AnyHttpUrl, FilePath
from fastapi import HTTPException

from app.config import get_settings
from app.schemas.mobsf import (
    DownloadSourceResponse,
    ScanResponse,
    Error,
    UploadResponse,
)


async def mobsf_upload_apk(
    mobsf_url: AnyHttpUrl,
    mobsf_secret: str,
    file_name: str,
    file_data: bytes,
):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            str(mobsf_url) + "api/v1/upload",
            headers={"Authorization": mobsf_secret},
            files={"file": (file_name, file_data)},
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=Error.model_validate_json(resp.content).error,
        )

    return UploadResponse.model_validate_json(resp.content).hash


async def mobsf_download_apk(mobsf_url: AnyHttpUrl, hash: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(str(mobsf_url) + f"download/{hash}.apk")

    return resp.read()


async def mobsf_scan_file(
    mobsf_url: AnyHttpUrl,
    mobsf_secret: str,
    hash: str,
):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            str(mobsf_url) + "api/v1/scan",
            headers={"Authorization": mobsf_secret},
            data={"hash": hash},
            timeout=300,
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=Error.model_validate_json(resp.content).error,
        )

    return ScanResponse.model_validate_json(resp.content)


async def mobsf_download_source_file(
    mobsf_url: AnyHttpUrl,
    mobsf_secret: str,
    hash: str,
    file: FilePath,
):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            str(mobsf_url) + "api/v1/view_source",
            headers={"Authorization": mobsf_secret},
            data={"hash": hash, "file": file, "type": "apk"},
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=Error.model_validate_json(resp.content).error,
        )

    return DownloadSourceResponse.model_validate_json(resp.content)
