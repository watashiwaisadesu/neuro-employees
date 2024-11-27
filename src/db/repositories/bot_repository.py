from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from src.db.models import Bot
from src.bot.responses import BotResponse
from pydantic import UUID4


class BotsRepository:
    @staticmethod
    async def create_bot(db: AsyncSession, user_uid: str, bot_type: str) -> Bot:
        bot = Bot(
            user_uid=user_uid,
            bot_type=bot_type,
            status="draft",  # Bot is still being set up
        )
        db.add(bot)
        await db.commit()
        await db.refresh(bot)
        return bot

    @staticmethod
    async def update_bot_settings(
            db: AsyncSession,
            bot_uid: str,
            name: str,
            description: str,
            context: str,
            creativity: float
    ) -> BotResponse:
        bot = await db.get(Bot, bot_uid)
        if not bot:
            raise NoResultFound("Bot not found")

        bot.name = name
        bot.description = description
        bot.context = context
        bot.creativity = creativity
        await db.commit()
        await db.refresh(bot)

        return BotResponse(
            uid=bot.uid,  # or whatever attribute corresponds to UUID
            bot_type=bot.bot_type,
            name=bot.name,
            description=bot.description,
            context=bot.context,
            creativity=bot.creativity,
            status=bot.status,
            integration_token = bot.integration_token,
        )

    @staticmethod
    async def get_bot_by_id(db: AsyncSession, bot_uid: str, user_uid: str = None) -> BotResponse:
        """
        Get a bot by its ID. If a user_uid is provided, check bot ownership.
        """
        query = select(Bot).where(Bot.uid == bot_uid)
        if user_uid:
            query = query.where(Bot.user_uid == user_uid)

        result = await db.execute(query)
        bot = result.scalars().first()

        if not bot:
            raise NoResultFound("Bot not found")

        return bot
