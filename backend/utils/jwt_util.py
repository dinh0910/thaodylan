from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config import CONST
from jose import ExpiredSignatureError , jwt

class JWTRepo:

    def __init__(self, data: dict = {}, token: str = None):
        self.data = data
        self.token = token

    def generate_token(self, expires_delta: Optional[timedelta] = timedelta(minutes=15)):
        to_encode = self.data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encode_jwt = jwt.encode(to_encode, CONST.JWT_SECRET_KEY, algorithm=CONST.JWT_ALGORITHM)
        return encode_jwt

    def decode_token(self):
        return jwt.decode(self.token, CONST.JWT_SECRET_KEY, algorithms=[CONST.JWT_ALGORITHM])
    
    def decode_token_middleware(token: str):
        return jwt.decode(token, CONST.JWT_SECRET_KEY, algorithms=[CONST.JWT_ALGORITHM])
    

class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)        
      
    async def __call__(self, request: Request):
     
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
                
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=401, detail={"status": "AccessDenied", "message": "Invalid authentication schema."})
            user = self.verify_jwt(credentials.credentials)
            user_ctx = dict(**user)
            user_ctx.pop("exp")
            
            return user
        else:
            raise HTTPException(
                status_code=401, detail={"status": "AccessDenied", "message": "Invalid authorization code."})
    
    def verify_jwt(self, jwt_token: str):
        try:
            return jwt.decode(jwt_token, CONST.JWT_SECRET_KEY, algorithms=[CONST.JWT_ALGORITHM], options={"verify_exp": True}) 
        except ExpiredSignatureError as e:
            raise HTTPException(status_code=403, detail={"status": "Forbidden", "message": str(e)})
        except Exception as e:
            raise HTTPException(status_code=401, detail={"status": "AccessDenied", "message": str(e)})
    
     
    
