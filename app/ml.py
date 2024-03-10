import asyncio
from pathlib import Path
import tempfile

from functools import lru_cache
from xmalplus import XmalPlus


@lru_cache
def get_xmal_model():
    return XmalPlus()


async def ml_classify_malware(
    xmal_plus: XmalPlus, apk_name: str, file_bytes: bytes
) -> tuple[float, dict[str, str]]:
    with tempfile.TemporaryDirectory(suffix="IVSR_") as apk_dir:
        apk_dir = Path(apk_dir)
        with open(apk_dir / apk_name, "wb") as apkfile:
            await asyncio.to_thread(apkfile.write, file_bytes)
            return await asyncio.to_thread(xmal_plus.run, str(apk_dir), apk_name)
