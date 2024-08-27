import logging
from jose import jwt, JWTError
from datetime import timedelta, datetime
from app.schemas import user_schema
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 1  # settings.ACCESS_TOKEN_EXPIRES_MINUTES
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")
logger = logging.getLogger(__name__)


async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception) -> user_schema.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            logger.error('Could not validate credentials')
            raise credentials_exception

        token_data = user_schema.TokenData(user_id=str(user_id))
    except JWTError as error:
        logger.error(error)
        raise HTTPException(status_code=401, detail=str(error))
    except Exception as error:
        logger.error(error)
        raise credentials_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could Not Validate credentials!",
                                          headers={"WWW-Authenticate": "Bearer"})

    return verify_access_token(token, credentials_exception)
