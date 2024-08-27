import logging
import psycopg2
from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.schemas import user_schemas
from app.db import connection
from app.core import utils
from app.core import security
from psycopg2 import sql

router = APIRouter(tags=['Login'])
logger = logging.getLogger(__name__)
cred_error = 'Invalid Credentials'


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary='Creating a new user in the database',
    response_model=user_schemas.UserOut
)
async def create_user(
        user_data: user_schemas.UserCreate,
        database_access: list = Depends(connection.get_db)):
    conn, cursor = database_access

    user_data.password = await utils.bcrypt_hash(user_data.password)

    try:
        user_data = user_data.model_dump()

        insert_query = sql.SQL("""
            INSERT INTO {table} ({fields})
            VALUES ({values})
            RETURNING *;
        """).format(
            table=sql.Identifier('users'),
            fields=sql.SQL(', ').join([
                sql.Identifier('email'),
                sql.Identifier('first_name'),
                sql.Identifier('last_name'),
                sql.Identifier('password')
            ]),
            values=sql.SQL(', ').join([sql.Placeholder(k) for k in user_data.keys()])
        )

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
    finally:
        conn.close()


@router.get('/me',
            summary="Checks the logged in user's details",
            description="Endpoint to check the user's details",
            status_code=status.HTTP_200_OK,
            )
async def get_current_user(current_user: user_schemas.TokenData = Depends(security.get_current_user)):
    return {'detail': 'user is logged in', 'user_id': current_user.user_id}
