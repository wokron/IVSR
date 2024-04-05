from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, AnyUrl


class Settings(BaseSettings):
    mobsf_secret: str
    mobsf_url: AnyHttpUrl

    qianfan_ak: str
    qianfan_sk: str

    sqlite_url: AnyUrl

    baidu_translate_ak: str
    baidu_translate_sk: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings():
    return Settings()
