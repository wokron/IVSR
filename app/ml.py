import asyncio
from pathlib import Path
import tempfile

from app.model import get_xmal_model


async def ml_classify_malware(
    apk_name: str, file_bytes: bytes
) -> tuple[float, dict[str, str]]:
    with tempfile.TemporaryDirectory(suffix="IVSR_") as apk_dir:
        apk_dir = Path(apk_dir)
        with open(apk_dir / apk_name, "wb") as apkfile:
            await asyncio.to_thread(apkfile.write(file_bytes))
            return await asyncio.to_thread(get_xmal_model().run(apk_dir, apk_name))
