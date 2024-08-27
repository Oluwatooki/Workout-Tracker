import logging
from fastapi import HTTPException, status, APIRouter, Depends, Request, Query
import psycopg2
import app.schemas.user_schema as user_schema
import app.db.connection as connection
import app.core.utils as utils

router = APIRouter(tags=['Users'])
logger = logging.getLogger(__name__)


@router.post("/register",
             status_code=status.HTTP_201_CREATED,
             summary='Creating a new user in the database',
             response_model=user_schema.UserOut
             )
async def create_user(
        user_data: user_schema.UserCreate,
        database_access: list = Depends(connection.get_db)):
    conn, cursor = database_access

    user_data.password = await utils.bcrypt_hash(user_data.password)

    try:
        user_data = user_data.model_dump()

        insert_query = """
                INSERT INTO users (email, first_name, last_name, password )
                VALUES (%(email)s, %(first_name)s, %(last_name)s, %(password)s )
                RETURNING *
            """

        cursor.execute(insert_query, user_data)
        new_user = cursor.fetchone()

    except psycopg2.errors.UniqueViolation as error:
        logger.warning(f"Attempt to create user with duplicate email: {user_data['email']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already in use")
    except Exception as e:
        logger.error(f"Error occurred while creating user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        conn.commit()
        logger.info(f"User created successfully: {new_user}")
        return new_user
