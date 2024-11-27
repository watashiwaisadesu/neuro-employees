from pydantic import BaseModel
from typing import List

# Data Models
class MessagingObject(BaseModel):
    sender: dict
    recipient: dict
    timestamp: int
    message: dict

class EntryObject(BaseModel):
    id: str
    time: int
    messaging: List[MessagingObject]

class WebhookObject(BaseModel):
    object: str
    entry: List[EntryObject]