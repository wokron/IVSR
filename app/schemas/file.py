from pydantic import BaseModel


class File(BaseModel):
    file: str
    data: str
    type: str
