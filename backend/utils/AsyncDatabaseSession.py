import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import Generic, TypeVar
from sqlalchemy import update as sql_update, delete as sql_delete
from sqlalchemy.future import select
from contextlib import asynccontextmanager
from utils.jwt_util import JWTRepo
from abc import ABCMeta

from config import CONST
from models import Base

SQLALCHEMY_DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL", "sqlite+aiosqlite:///sql_app.db"
)


class Singleton(ABCMeta, type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call method for the singleton metaclass."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


T = TypeVar("T")


class AsyncDatabaseSession(metaclass=Singleton):

    def __init__(self) -> None:
        self.session = None
        self.engine = None
        self.init()

    def __getattr__(self, name):
        return getattr(self.session, name)

    def init(self):
        self.engine = create_async_engine(
            SQLALCHEMY_DATABASE_URL, future=True, echo=False
        )

        self.session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def commit_rollback(self):
        try:
            await self.commit()
        except Exception:
            await self.rollback()
            raise
        finally:
            await self.close()

    @asynccontextmanager
    async def get_session(self, token: str = None, isCommit: bool = False):
        async with self.session() as ss:
            try:
                yield ss
                if isCommit:
                    ss.commit()
            except Exception as e:
                await ss.rollback()
                raise
            finally:
                try:
                    await ss.close()
                except:
                    pass


dbContext = AsyncDatabaseSession


class BaseRepository:
    model = Generic[T]

    @classmethod
    async def create(cls, **kwargs):
        ctxdb = dbContext()
        async with ctxdb.get_session() as ctx:
            model = cls.model(**kwargs)
            ctx.add(model)
            await ctx.commit()
            return model

    @classmethod
    async def get_all(cls):
        ctxdb = dbContext()
        async with ctxdb.get_session() as ctx:
            query = select(cls.model)
            return (await ctx.execute(query)).scalars().all()

    @classmethod
    async def get_by_id(cls, model_id: str):
        ctxdb = dbContext()
        async with ctxdb.get_session() as ctx:
            query = select(cls.model).where(cls.model.id == model_id)
            return (await ctx.execute(query)).scalar_one_or_none()

    @classmethod
    async def update(cls, model_id: str, **kwargs):
        ctxdb = dbContext()
        async with ctxdb.get_session() as ctx:
            query = (
                sql_update(cls.model)
                .where(cls.model.id == model_id)
                .values(**kwargs)
                .execution_options(synchronize_session="fetch")
            )
            value = await ctx.execute(query)
            await ctx.commit()
            return value.rowcount

    @classmethod
    async def delete(cls, model_id: str):
        ctxdb = dbContext()
        async with ctxdb.get_session() as ctx:
            query = sql_delete(cls.model).where(cls.model.id == model_id)
            value = await ctx.execute(query)
            await ctx.commit()
            return value.rowcount

    @staticmethod
    async def get_one(query: any):
        ctxdb = dbContext()
        async with ctxdb.get_session() as ctx:
            return (await ctx.execute(query)).scalar_one_or_none()

    @staticmethod
    async def get_all(query: any):
        ctxdb = dbContext()
        async with ctxdb.get_session() as ctx:
            return (await ctx.execute(query)).scalars().all()
