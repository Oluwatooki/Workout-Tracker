import logging

from fastapi import HTTPException,status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

logging.getLogger("passlib").setLevel(logging.CRITICAL)


async def bcrypt_hash(password: str):
    hashed_password = pwd_context.hash(password)
    return hashed_password


async def verify_login_details(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def update_missed_workouts(user_id: str, database_access: list):
    conn, cursor = database_access

    update_status_query = """
    UPDATE scheduled_workouts
    SET status = 'missed'
    WHERE status = 'pending' AND (scheduled_date < CURRENT_DATE OR 
    (scheduled_date = CURRENT_DATE AND scheduled_time < CURRENT_TIME))
    AND user_id = %s;
    """

    try:
        cursor.execute(update_status_query, (user_id,))
        conn.commit()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error occurred while updating missed workouts: {str(error)}")
