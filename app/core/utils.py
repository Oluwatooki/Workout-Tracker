import logging

from fastapi.security import APIKeyHeader
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


logging.getLogger("passlib").setLevel(logging.CRITICAL)


async def bcrypt_hash(password: str):
    hashed_password = pwd_context.hash(password)
    return hashed_password


async def verify_login_details(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
