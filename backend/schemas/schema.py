from pydantic import BaseModel

class ResponseDetail(BaseModel):
    status_code: int = 200
    message: str
    data: dict = None
