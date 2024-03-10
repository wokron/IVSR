from typing import Optional
from sqlmodel import Field, SQLModel


class AndroidAppCreate(SQLModel):
    hash: str = Field(..., primary_key=True)
    name: str
    data: bytes


class AndroidApp(SQLModel, table=True):
    hash: str = Field(..., primary_key=True)
    name: str
    data: bytes
    static_result: Optional[str] = Field(None)
    ml_result: Optional[str] = Field(None)
    llm_report: Optional[str] = Field(None)
