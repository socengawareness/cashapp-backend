# app/models.py

from pydantic import BaseModel


class Login(BaseModel):
    login_number: str  # 11-digit number
    device_id: str


class AddUser(BaseModel):
    login_number: str


class User(BaseModel):
    user_email: str
    login_number: str
