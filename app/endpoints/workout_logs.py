import logging

import psycopg2
from fastapi import HTTPException, status, APIRouter, Depends, Request, Query
from app.schemas import users_schemas, logs_schemas
from app.db import connection
from app.core import security, utils
from psycopg2 import sql

router = APIRouter(tags=["Workout Logs"])
logger = logging.getLogger(__name__)


@router.post(
    "/workout-logs",
    status_code=status.HTTP_201_CREATED,
    summary="Log a workout.",
    response_model=logs_schemas.WorkoutLogOut,
)
async def create_workout_log(
    workout_log: logs_schemas.WorkoutLogCreate,
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):
    # conn, cursor = database_access
    user_id = current_user.user_id

    insert_log_query = sql.SQL(
        """
        INSERT INTO workout_logs (user_id, scheduled_workout_id,completed_at, total_time, notes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING log_id, user_id, scheduled_workout_id, completed_at, total_time, notes;
    """
    )

    with database_access as (conn, cursor):

        try:
            cursor.execute(
                insert_log_query,
                (
                    user_id,
                    workout_log.scheduled_workout_id,
                    workout_log.completed_at,
                    workout_log.total_time,
                    workout_log.notes,
                ),
            )
            log_out = cursor.fetchone()

        except psycopg2.errors.ForeignKeyViolation as error:
            logger.error(
                f"Error occurred while logging a scheduled workout: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error logging workout: scheduled Workout Not Found "
            )

        except Exception as error:
            logger.error(
                f"Error occurred while logging a scheduled workout: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error logging workout {error}",
            )

        logger.info(
            "Workout Log successfully Created",
            exc_info=True,
        )

        conn.commit()
        return log_out


@router.get(
    "/workout-logs",
    status_code=status.HTTP_200_OK,
    summary="List all workout logs for the current User",
    response_model=list[logs_schemas.WorkoutLogOut],
)
async def list_workout_logs(
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
    limit: int = 10,
    skip: int = 0,
):

    user_id = current_user.user_id

    select_logs_query = sql.SQL(
        """
        SELECT log_id, user_id, scheduled_workout_id, completed_at, total_time, notes
        FROM workout_logs
        WHERE user_id = %s
        LIMIT %s
        OFFSET %s;
    """
    )

    with database_access as (conn, cursor):
        try:
            cursor.execute(select_logs_query, (user_id, limit, skip))
            logs = cursor.fetchall()
        except Exception as error:
            logger.error(
                f"Error occurred while getting a list of all workout logs: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        if not logs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No workout logs found for the user.",
            )

        return logs


@router.get(
    "/workout-logs/{log_id}",
    status_code=status.HTTP_200_OK,
    summary="List a specific workout log for the current User",
    response_model=logs_schemas.WorkoutLogOut,
)
async def list_workout_logs(
    log_id: str,
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):

    user_id = current_user.user_id

    select_logs_query = sql.SQL(
        """
        SELECT log_id, user_id, scheduled_workout_id, completed_at, total_time, notes
        FROM workout_logs
        WHERE user_id = %s AND log_id = %s
    """
    )

    with database_access as (conn, cursor):
        try:
            cursor.execute(select_logs_query, (user_id,log_id))
            logs = cursor.fetchone()
        except Exception as error:
            logger.error(
                f"Error occurred while getting a specific of workout log: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        if not logs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No workout log found for the user.",
            )

        return logs
