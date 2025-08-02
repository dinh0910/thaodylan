from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()

class StatusResponse(BaseModel):
    status: str = "Ok"
    
@router.get("/status")
def status() -> StatusResponse:
    
    return StatusResponse(status="Ok")    