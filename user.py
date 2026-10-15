# schemas/user.py
# Schemas (DTOs) describe what data an endpoint accepts or returns.
# Pydantic checks the data automatically and rejects bad requests with a 422.
from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    fullname: str
    email: str
    password: str
    location: str | None = None
    age: int


class UpdateUserDTO(BaseModel):
    # everything is optional because a PATCH only sends the fields being changed
    fullname: str | None = None
    email: str | None = None
    password: str | None = None
    location: str | None = None
    age: int | None = None


class LoginDTO(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    # what we send BACK. Notice there is no password field here on purpose.
    id: int
    fullname: str
    email: str
    location: str | None = None
    age: int
