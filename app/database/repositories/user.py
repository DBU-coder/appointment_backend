from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Role, User
from app.database.repositories.abstract import Repository

if TYPE_CHECKING:
    from app.api.v1.users.schemas import UserInDB


class UserRepository(Repository[User]):

    def __init__(self, session: AsyncSession):
        super().__init__(type_model=User, session=session)

    async def new(self, user_data: "UserInDB") -> User:
        new_user = await self.session.merge(User(**user_data.model_dump()))
        await self.session.commit()
        return new_user

    async def get_superadmin(self) -> User | None:
        return await self.get_by_filter(role=Role.SUPERADMIN)
