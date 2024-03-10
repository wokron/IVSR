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
    ml_report: Optional[str] = Field(None)
