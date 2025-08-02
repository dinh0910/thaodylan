from fastapi import APIRouter, Security
from schemas.auth_schema import TokenSecretRequest, TokenResponse, LoginRequest
from services.auth_service import AuthService
from utils.jwt_util import JWTBearer

router = APIRouter(prefix="/auth", tags=["Authentications"])

@router.post("/auth-login")
async def auth_login(request: LoginRequest):
    return await AuthService().auth_login(request)

@router.post("/auth-register")
async def auth_register(request: LoginRequest):
    return await AuthService().auth_register(request)

@router.post("/app-token", response_model=TokenResponse)
async def get_JWT_by_secret_key(tokenSecret: TokenSecretRequest) -> TokenResponse:
    response = await AuthService().get_jwt_by_secret_key(tokenSecret)
    return response

@router.get("/refresh-token")
async def refresh_JWT(user: dict = Security(JWTBearer())) -> TokenResponse:
    response = await AuthService().refresh_jwt(user)
    return response