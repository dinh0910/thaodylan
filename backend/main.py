from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv
from config import CONST
from startup import startup_app
from utils.AsyncDatabaseSession import dbContext

origins = ["*"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     🚀 App is starting up...")
    startup_app(app)
    await dbContext().create_all()

    yield
    
    print("INFO:     🛑 App is shutting down...")

def init_app():
    application = FastAPI(
        title="Sample Management API - Slope",
        description="",
        version="1.0",
        lifespan=lifespan
    )
    default_limit = f"{CONST.LIMIT_REQUESTS}/minute"
    limiter = Limiter(key_func=get_remote_address, default_limits=[default_limit])
    application.state.limiter = limiter
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.add_middleware(SlowAPIMiddleware)
    return application

load_dotenv()

app = init_app()
