# schemas/talent.py
from typing import Literal
from pydantic import BaseModel

# the four categories shown on the landing page. Anything else is rejected with a 422.
Category = Literal["Photography", "Sculpture", "Graphic Design", "Fine Art"]


class CreateTalentDTO(BaseModel):
    user_id: int
    category: Category
    bio: str | None = None


class TalentOut(BaseModel):
    id: int
    user_id: int
    fullname: str
    location: str | None = None
    category: str
    bio: str | None = None
