from app.schemas import mobsf, resp
from app.tests.schemas.utils import json_data


def test_mobsf_decode():
    mobsfResp = mobsf.ScanResponse.model_validate_json(json_data)
    scanResp = resp.StaticScanResult.from_mobsf(mobsfResp)
