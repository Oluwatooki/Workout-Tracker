import datetime
import logging
import string
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator, Field
logger = logging.getLogger(__name__)


class UserBase(BaseModel):
    email: EmailStr = Field(..., example="mikey@example.com")
    first_name: str = Field(..., example="Mike")
    last_name: str = Field(..., example="Ekim")


class UserCreate(UserBase):
    password: str = Field(..., example="1%0TmlkiA220")

    @field_validator("password")
    def check_password_strength(cls, password):
        password_len = 8
        if len(password) < password_len:
            error = f"Password must me at least {password_len} characters long"
            logger.error(error)
            raise ValueError(error)
        special_characters = set(string.punctuation)
        uppercase_count = sum(1 for char in password if char.isupper())
        lowercase_count = sum(1 for char in password if char.islower())
        special_char_count = sum(1 for char in password if char in special_characters)
        num_count = sum(1 for char in password if char.isdigit())
        if (
            special_char_count < 1
            or uppercase_count < 1
            or num_count < 1
            or lowercase_count < 1
        ):
            error = """The password must have at least 1 special character,
                            1 uppercase character, 1 digit and one lowercase character"""
            logger.error(error)
            raise ValueError(error)
        return password


class UserOut(UserBase):
    user_id: UUID
    created_date: datetime.datetime


class Token(BaseModel):
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYmE5N2JjMmYtYmI0Yi00NGU4LTg4YTAtM2M1NThhZTQxMWZjIiwiZXhwIjoxNzI1Mjc2MzAyfQ.TCBb30lAim_flZoHRb838VQx3bJjfCrTQf26Hc5Qt70",
    )
    token_type: str = Field(..., example="bearer")


class TokenData(BaseModel):
    """Token Data"""

    user_id: str | None = None
