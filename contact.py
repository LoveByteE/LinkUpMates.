# schemas/contact.py
from pydantic import BaseModel


class ContactDTO(BaseModel):
    name: str
    email: str
    message: str
