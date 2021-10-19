from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.util.concurrency import greenlet_spawn
from sqlalchemy_utils import create_database, database_exists
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette_context import context
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential
from uvicorn.config import logger

from joj.horse.config import settings


@lru_cache()
def get_db_engine() -> AsyncEngine:
    db_url = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_username,
        password=settings.db_password,
        database=settings.db_name,
    )
    engine = create_async_engine(db_url, future=True, echo=True)
    return engine


@asynccontextmanager
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # if a session is created for the request, use it directly
    if context.exists() and "db_session" in context:
        try:
            yield context["db_session"]
        finally:
            pass
    # otherwise, create a new session
    else:
        session = AsyncSession(get_db_engine())
        try:
            yield session
        finally:
            await session.close()


async def db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    # create a session for each request
    async with db_session() as session:
        context["db_session"] = session
        yield session


async def ensure_db() -> None:
    engine = get_db_engine()
    if not await greenlet_spawn(database_exists, engine.url):
        logger.info("Database %s created.", settings.db_name)
        await greenlet_spawn(create_database, engine.url)
    else:
        logger.info("Database %s already exists.", settings.db_name)


async def generate_schema() -> None:
    async with get_db_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("SQLModel generated schema.")


@retry(stop=stop_after_attempt(5), wait=wait_exponential(2))
async def try_init_db() -> None:
    attempt_number = try_init_db.retry.statistics["attempt_number"]
    try:
        await ensure_db()
        if settings.debug:
            await generate_schema()
    except Exception as e:
        max_attempt_number = try_init_db.retry.stop.max_attempt_number
        msg = "Tortoise-ORM: initialization failed ({}/{})".format(
            attempt_number, max_attempt_number
        )
        if attempt_number < max_attempt_number:
            msg += ", trying again after {} second.".format(2 ** attempt_number)
        else:
            msg += "."
        logger.exception(e)
        logger.warning(msg)
        raise e
