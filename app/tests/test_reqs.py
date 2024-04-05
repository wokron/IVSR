from app.config import get_settings
from app.reqs import baidu_translate


def test_baidu_translate():
    settings = get_settings()
    result = baidu_translate(
        settings.baidu_translate_ak,
        settings.baidu_translate_sk,
        "en",
        "zh",
        "SECURITY ANALYSIS REPORT\n==============================\n\nIntroduction",
    )
    assert len(result) != 0
