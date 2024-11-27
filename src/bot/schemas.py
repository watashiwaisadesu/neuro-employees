from pydantic import BaseModel, UUID4
from typing import Optional


class BotTypeRequest(BaseModel):
    bot_type: str  # Тип: "consultant", "smm", "seller"


class BotSettingsRequest(BaseModel):
    name: str
    description: str
    context: str
    creativity: float  # 0.0 - минимальная креативность, 1.0 - максимальная


class BotIntegrationRequest(BaseModel):
    platform: str  # "telegram" или "whatsapp"


class BotBase(BaseModel):
    bot_type: str
    name: str
    description: str
    context: str
    creativity: float


