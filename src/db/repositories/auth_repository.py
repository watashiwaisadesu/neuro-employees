from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import User
from src.utils.security import generate_passwd_hash
from src.auth.schemas import UserCreateModel

class AuthRepository:
    # Retrieve user by email
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.execute(statement)  # Using execute instead of exec

        user = result.scalars().first()  # Use scalars() to get the first User object directly

        return user


    # Check if a user already exists
    async def user_exists(self, email, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user is not None else False


    # Create a new user
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        password = str(user_data_dict.pop("password", None)) # Remove password from dictionary

        new_user = User(**user_data_dict)

        if password:
            new_user.password_hash = generate_passwd_hash(password)  # Assign the hashed password manually
        new_user.role = "user"

        session.add(new_user)
        await session.commit()

        return new_user


    async def update_user(self, user:User , user_data: dict,session:AsyncSession):

        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()

        return user
