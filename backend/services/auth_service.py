import uuid
from datetime import timedelta
from fastapi import HTTPException
from config import CONST
from repositories.user_repo import UserRepository
from schemas.auth_schema import TokenResponse, TokenSecretRequest, LoginRequest
from schemas.schema import ResponseDetail
from utils.jwt_util import JWTRepo
from utils.AsyncDatabaseSession import dbContext
from models import User
from sqlalchemy import desc, asc, select, func, update, cast, String
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    '''
    This class is responsible for the business logic of the authentication service.
    '''
    def __init__(self):
        pass

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    async def auth_login(self, user_data: LoginRequest) -> TokenResponse:
        ctxdb = dbContext()
        async with ctxdb.get_session() as ctx:
            query = (
                await ctx.execute(
                    select(User)
                    .where(
                        user_data.email == User.email
                    )
                )
            ).scalars().first()

            check_pw = AuthService.verify_password(user_data.password, query.password)
            
            if query is None:
                raise HTTPException(status_code=404, detail="User not found")
            elif not check_pw:
                raise HTTPException(status_code=404, detail="Password is incorrect")

            data = {
                "id": query.id,
                "email": query.email,
            }
            token = JWTRepo(data=data).generate_token(expires_delta=timedelta(seconds=CONST.EXPIRE_IN))
            return TokenResponse(access_token=token)
        
    async def auth_register(self, user_data: LoginRequest) -> ResponseDetail:
        ctxdb = dbContext()
        async with ctxdb.get_session() as ctx:
            query_check_user = (
                await ctx.execute(
                    select(User)
                    .where(
                        user_data.email == User.email
                    )
                )
            ).scalars().first()
            
            if query_check_user:
                raise HTTPException(status_code=404, detail="User is existed")
            
            data_req = {
                "id": str(uuid.uuid4()),
                "user_name": user_data.email,
                "email": user_data.email,
                "password": AuthService.get_password_hash(user_data.password)
            }

            ctx.add(User(**data_req))
            await ctx.commit()
            return ResponseDetail(message="Register account successful")

    async def get_data_by_email(self, email: str):
        '''
        This method is responsible for returning the data that will be used to generate the JWT token.
        '''
        user = await UserRepository().get_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "email": user.email,
            "id": user.id
        }

    async def get_jwt_by_secret_key(self, tokenSecret: TokenSecretRequest) -> TokenResponse:
        '''
        This method is responsible for generating a JWT token.
        '''
        if tokenSecret.app_key != CONST.REQUEST_SECRET_KEY:
            raise HTTPException(status_code=401, detail="Invalid secret key")
        
        data = await self.get_data_by_email(tokenSecret.email)
        token = JWTRepo(data=data).generate_token(expires_delta=timedelta(seconds=CONST.EXPIRE_IN))
        return TokenResponse(access_token=token)
    
    async def refresh_jwt(self, user: dict) -> TokenResponse:
        '''
        This method is responsible
        '''
        token = JWTRepo(data=user).generate_token(expires_delta=timedelta(seconds=CONST.EXPIRE_IN))
        return TokenResponse(access_token=token)