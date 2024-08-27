import logging

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
logging.getLogger("passlib").setLevel(logging.CRITICAL)


async def bcrypt_hash(password: str):
    hashed_password = pwd_context.hash(password)
    return hashed_password
