import httpx
from pydantic import AnyHttpUrl, FilePath
from fastapi import HTTPException

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


async def mobsf_download_file(mobsf_url: AnyHttpUrl, filename):
    async with httpx.AsyncClient() as client:
        resp = await client.get(str(mobsf_url) + f"download/{filename}")

    return resp.read()


async def mobsf_scan_apk(
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


def baidu_translate(ak: str, sk: str, from_lang: str, to_lang: str, content: str):

    def get_access_token():
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": ak,
            "client_secret": sk,
        }
        return str(httpx.post(url, params=params).json().get("access_token"))

    url = (
        "https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token="
        + get_access_token()
    )

    result = []
    for line in content.split("\n"):
        if len(line) == 0:
            result.append("")
            continue
        response = httpx.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "from": from_lang,
                "to": to_lang,
                "q": line,
            },
        )

        result.append(response.json()["result"]["trans_result"][0]["dst"])

    return "\n".join(result)
