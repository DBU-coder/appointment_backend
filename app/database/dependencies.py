from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Database, db_connector


async def get_database(
    session: Annotated[AsyncSession, Depends(db_connector.get_session)]
) -> Database:
    print("get_database")
    return Database(session)
