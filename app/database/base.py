from collections.abc import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

from .repositories import UserRepository
from .repositories.patient import PatientRepository


class DBConnector:
    engine: AsyncEngine

    def __init__(self, url: URL | str, echo: bool = False) -> None:
        self.url = url
        self.echo = echo
        self.engine = self.__create_engine()
        self.session_factory = self.__create_session_maker()

    def __create_engine(self) -> AsyncEngine:
        return create_async_engine(
            url=self.url,
            echo=self.echo,
        )

    def __create_session_maker(self) -> async_sessionmaker:
        return async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


class Database:
    session: AsyncSession
    user: UserRepository

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
        self.user = UserRepository(session=session)
        self.patient = PatientRepository(session=session)


db_connector = DBConnector(url=settings.database_url, echo=settings.DB_ECHO)
