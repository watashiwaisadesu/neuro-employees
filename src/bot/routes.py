from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.core.database_setup import get_async_db
from src.db.repositories.bot_repository import BotsRepository
from src.db.models import User
from src.bot.service import generate_bot_response
from src.bot.integrations import TelegramIntegration, WhatsAppIntegration, InstagramIntegration
from src.bot.schemas import (
    BotTypeRequest,
    BotSettingsRequest,
    BotIntegrationRequest,
)
from src.bot.responses import (
    BotTypeResponse,
    BotSettingsResponse,
    CompleteBotResponse,
)


bots_router = APIRouter()

@bots_router.post("/select", response_model=BotTypeResponse)
async def select_bot_type(
    bot_data: BotTypeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Выбор типа бота.
    """
    new_bot = await BotsRepository.create_bot(
        db=db,
        user_uid=current_user.uid,
        bot_type=bot_data.bot_type
    )
    return {"uid": new_bot.uid, "message": "Bot type selected successfully"}


@bots_router.patch("/{bot_uid}/settings", response_model=BotSettingsResponse)
async def update_bot_settings(
        bot_uid: str,
        settings: BotSettingsRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db),
):
    """
    Настройка параметров бота.
    """
    bot = await BotsRepository.get_bot_by_id(db=db, bot_uid=bot_uid, user_uid=current_user.uid)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    updated_bot = await BotsRepository.update_bot_settings(
        db=db,
        bot_uid=bot_uid,
        name=settings.name,
        description=settings.description,
        context=settings.context,
        creativity=settings.creativity
    )
    return {"message": "Bot settings updated successfully", "bot": updated_bot.dict()}


@bots_router.websocket("/playground/{bot_uid}")
async def bot_playground(
        websocket: WebSocket,
        bot_uid: str,
        db: AsyncSession = Depends(get_async_db),
):
    """
    WebSocket для тестирования бота.
    """
    bot = await BotsRepository.get_bot_by_id(db=db, bot_uid=bot_uid)
    if not bot:
        await websocket.close(code=1000)
        return

    await websocket.accept()
    while True:
        user_message = await websocket.receive_text()
        bot_response = await generate_bot_response(bot.context, user_message, bot.creativity)
        await websocket.send_text(bot_response)


@bots_router.post("/{bot_uid}/complete", response_model=CompleteBotResponse)
async def complete_bot_setup(
        bot_uid: str,
        integration: BotIntegrationRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db),
):
    """
    Complete bot setup and integrate with platforms.
    """
    bot = await BotsRepository.get_bot_by_id(db=db, bot_uid=bot_uid, user_uid=current_user.uid)

    # Check if the bot exists and is in draft status
    if not bot or bot.status != "draft":
        raise HTTPException(status_code=400, detail="Bot setup is incomplete or invalid")

    # Integration with Telegram/WhatsApp
    if integration.platform == "telegram":
        integration_token = await TelegramIntegration.create_bot(bot.name)
        # Update status and save
        bot.status = "active"
        bot.integration_token = integration_token
        await db.commit()
        await db.refresh(bot)
        return CompleteBotResponse(message="Bot setup complete", integration_token=integration_token)
    elif integration.platform == "whatsapp":
        integration_token = await WhatsAppIntegration.create_bot(bot.name)
        # Update status and save
        bot.status = "active"
        bot.integration_token = integration_token
        await db.commit()
        await db.refresh(bot)
        return CompleteBotResponse(message="Bot setup complete", integration_token=integration_token)
    elif integration.platform == "instagram":
        # Generate the authorization URL for Instagram OAuth
        authorization_url = await InstagramIntegration.create_bot(bot.uid)
        # Return the authorization URL to the frontend
        return CompleteBotResponse(
            message="Authorization URL generated",
            authorization_url=authorization_url
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid platform")