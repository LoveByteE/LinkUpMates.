# schemas/concept.py
from pydantic import BaseModel


class ConceptOut(BaseModel):
    id: int
    title: str
    tagline: str
    image_url: str | None = None
    page: str | None = None
