from pydantic import BaseModel, UUID4
from typing import Optional

class BotTypeResponse(BaseModel):
    uid: UUID4
    message: str

class BotSettingsResponse(BaseModel):
    message: str
    bot: dict  # JSON с данными обновлённого бота

class CompleteBotResponse(BaseModel):
    message: str
    integration_token: Optional[str] = None
    authorization_url: Optional[dict] = None

class BotResponse(BaseModel):
    uid: UUID4
    bot_type: str
    name: str
    description: str
    context: str
    creativity: float
    status: str
    integration_token: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True