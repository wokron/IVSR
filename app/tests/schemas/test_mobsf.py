from app.schemas import mobsf
from app.tests.schemas.utils import json_data


def test_mobsf_decode():
    mobsf.ScanResponse.model_validate_json(json_data)
