import logging
from fastapi import HTTPException, status, APIRouter, Depends
import psycopg2
from app.schemas import users_schemas
from app.db import connection
from app.core import utils
from psycopg2 import sql

router = APIRouter(tags=["Users"])
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Creating a new user in the database",
    response_model=users_schemas.UserOut,
)
async def create_user(
    user_data: users_schemas.UserCreate,
    database_access: list = Depends(connection.get_db),
):
    with database_access as (conn, cursor):
        user_data.password = await utils.bcrypt_hash(user_data.password)

        try:
            user_data = user_data.model_dump()

            insert_query = sql.SQL(
                """
                    INSERT INTO {table} ({fields})
                    VALUES ({values})
                    RETURNING *;
                """
            ).format(
                table=sql.Identifier("users"),
                fields=sql.SQL(", ").join(
                    [
                        sql.Identifier("email"),
                        sql.Identifier("first_name"),
                        sql.Identifier("last_name"),
                        sql.Identifier("password"),
                    ]
                ),
                values=sql.SQL(", ").join(
                    [sql.Placeholder(k) for k in user_data.keys()]
                ),
            )

            cursor.execute(insert_query, user_data)
            new_user = cursor.fetchone()

        except psycopg2.errors.UniqueViolation as error:
            logger.warning(
                f"Attempt to create user with duplicate email: {user_data['email']}",
                exc_info=True,
                extra={"user_email": user_data.email},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        except Exception as error:
            logger.error(
                f"Error occurred while creating user: {str(error)}",
                exc_info=True,
                extra={"user_email": user_data.email},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        conn.commit()
        logger.info(
            f"User created successfully: {new_user['user_id']}",
            exc_info=True,
            extra={"user_email": user_data["email"]},
        )
        return new_user
