from datetime import datetime
from pydantic import BaseModel, ConfigDict
class MessageBase(BaseModel):
    sender : str
    content:str
class MessageCreate(MessageBase):
    room_id: str
class MessageResponse(MessageBase):
    id: int
    room_id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)