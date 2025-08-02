from sqlalchemy.future import select
from utils.AsyncDatabaseSession import BaseRepository
from models import User

class UserRepository(BaseRepository):
    model = User

    @classmethod
    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        return await self.get_one(query)
