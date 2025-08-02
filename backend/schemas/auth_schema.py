from pydantic import BaseModel

from config import CONST

class TokenSecretRequest(BaseModel):
    '''
    This class is responsible for validating the request body of the get_JWT_by_secret_key endpoint.
    '''
    email: str = "demo@example.com"
    app_key: str


class TokenResponse(BaseModel):
    '''
    This class is responsible for validating the response body of the get_JWT_by_secret_key endpoint.
    '''
    access_token: str
    token_type: str = "bearer"
    expires_in: int = CONST.EXPIRE_IN

class LoginRequest(BaseModel):
    email: str
    password: str