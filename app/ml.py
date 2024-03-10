from pathlib import Path
import tempfile

from functools import lru_cache
from typing import Any
from xmalplus import XmalPlus


@lru_cache
def get_xmal_model():
    return XmalPlus()


async def ml_classify_malware(
    xmal_plus: XmalPlus, apk_name: str, file_bytes: bytes
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(suffix="IVSR_") as apk_dir:
        apk_dir = Path(apk_dir)
        apk_file = apk_dir / apk_name
        apk_file.write_bytes(file_bytes)
        return xmal_plus.run(str(apk_dir), apk_name)
