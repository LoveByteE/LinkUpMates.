# schemas/collaboration.py
from typing import Literal
from pydantic import BaseModel


class CreateCollabDTO(BaseModel):
    sender_id: int
    receiver_id: int
    message: str


class UpdateCollabDTO(BaseModel):
    # Literal means only these two words are accepted, anything else gets a 422
    status: Literal["accepted", "declined"]


class InboxItemOut(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    message: str
    status: str
    created_at: str


class OutboxItemOut(BaseModel):
    # same idea as the inbox, but we show who the request was sent TO
    id: int
    receiver_id: int
    receiver_name: str
    message: str
    status: str
    created_at: str
