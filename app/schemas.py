"""
Esquemas Pydantic.

Validan y dan forma a los datos que entran y salen por la API REST.
Pydantic garantiza que un registro tenga usuario, email y contraseña con
el formato correcto antes de tocar la base de datos.
"""
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
