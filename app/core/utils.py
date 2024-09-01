import logging

from fastapi import HTTPException, status
from passlib.context import CryptContext
from psycopg2 import sql

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)
logging.getLogger("passlib").setLevel(logging.CRITICAL)


async def bcrypt_hash(password: str):
    hashed_password = pwd_context.hash(password)
    return hashed_password


async def verify_login_details(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def update_missed_workouts(user_id: str, conn, cursor):

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error occurred while updating missed workouts: {str(error)}",
        )


async def fetch_plan_with_exercises(plan_id: str, user_id: str, cursor) -> dict:
    # Fetch the plan details
    select_plan_query = sql.SQL(
        """
        SELECT plan_id, user_id, name AS plan_name, description, created_at, updated_at
        FROM workout_plans
        WHERE user_id = %s AND plan_id = %s;
    """
    )

    select_plan_exercises_query = sql.SQL(
        """
        SELECT *
        FROM workout_plan_exercises
        WHERE plan_id = %s;
    """
    )
    try:
        cursor.execute(
            select_plan_query,
            (
                user_id,
                plan_id,
            ),
        )
        plan = cursor.fetchone()
    except Exception as error:
        logger.error(f"Error occurred: {str(error)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No workout plans found for the user.",
        )


    try:
        cursor.execute(select_plan_exercises_query, (plan["plan_id"],))
        exercises = cursor.fetchall()
        for x, exercise in enumerate(exercises):
            select_query = sql.SQL(
                """SELECT name AS exercise_name, description, category 
                                      FROM exercises WHERE exercise_id = %s"""
            )
            cursor.execute(select_query, (exercise["exercise_id"],))

            exercise_extra_info = dict(cursor.fetchone())
            exercises[x].update(**exercise_extra_info)
        plan.update({"exercises": exercises})
        plan.update({"metadata": {"exercise_count": len(exercises)}})
    except Exception as error:
        logger.error(f"Error occurred: {str(error)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )

    return plan
