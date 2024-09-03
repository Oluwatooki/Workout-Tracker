import logging
from typing import Annotated

from fastapi import HTTPException, status, APIRouter, Depends, Request, Query, Body
from app.core.utils import fetch_plan_with_exercises
from app.schemas import users_schemas, scheduled_workouts_schemas
from app.db import connection
from app.core import security, utils, examples, docs
from psycopg2 import sql

# Setup router and logging
router = APIRouter(tags=["Scheduled Workout Management"])
logger = logging.getLogger(__name__)


@router.post(
    "/scheduled-workouts",
    status_code=status.HTTP_201_CREATED,
    summary="Schedule a workout.",
    response_model=scheduled_workouts_schemas.ScheduledWorkoutOut,
    description=docs.create_workout_schedule
)
async def create_workout_schedule(
    scheduled_workout: Annotated[scheduled_workouts_schemas.ScheduledWorkoutCreate,Body
        (openapi_examples=examples.workout_schedule_examples)],
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):
    user_id = current_user.user_id

    # SQL query to verify if the workout plan exists for the user
    plan_id_check_query = sql.SQL(
        """
        SELECT plan_id
        FROM workout_plans
        WHERE user_id = %s AND plan_id = %s
        """
    )

    # SQL query to insert the scheduled workout into the database
    insert_schedule_query = sql.SQL(
        """
        INSERT INTO scheduled_workouts (plan_id, user_id, scheduled_date, scheduled_time, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *;
        """
    )

    with database_access as (conn, cursor):
        try:
            # Check if the workout plan exists and belongs to the user
            cursor.execute(plan_id_check_query, (user_id, scheduled_workout.plan_id))
            plan_id_verification = cursor.fetchone()
        except Exception as error:
            logger.error(
                f"Error occurred while checking plan_id: {str(error)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        if not plan_id_verification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workout Plan Not Found"
            )

        try:
            # Insert the scheduled workout into the database
            cursor.execute(
                insert_schedule_query,
                (
                    scheduled_workout.plan_id,
                    user_id,
                    scheduled_workout.scheduled_date,
                    scheduled_workout.scheduled_time,
                    scheduled_workout.status,
                ),
            )
            workout_schedule_out = cursor.fetchone()
        except Exception as error:
            logger.error(
                f"Error occurred while scheduling the workout: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        # Fetch the details of the workout plan including the exercises
        plan_details = await fetch_plan_with_exercises(
            scheduled_workout.plan_id, user_id, cursor
        )

        # Attach the plan details to the scheduled workout output
        workout_schedule_out.update({"plan_details": plan_details})

        conn.commit()

        return workout_schedule_out


@router.get(
    "/scheduled-workouts",
    status_code=status.HTTP_200_OK,
    summary="List all scheduled workouts for the authenticated user.",
    response_model=list[scheduled_workouts_schemas.ScheduledWorkoutOut],
    description=docs.list_workout_schedules,
)
async def get_workout_schedules(
    workout_status: scheduled_workouts_schemas.StatusChoice,
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
    limit: int = 10,
    skip: int = 0,
):

    user_id = current_user.user_id

    # Conditionally add the status filter if it's not set to 'all'
    all_or_something = "AND status = %s" if workout_status != "all" else " "

    # SQL query to retrieve scheduled workouts with optional status filtering
    workout_schedule_query = f"""
        SELECT *
        FROM scheduled_workouts
        WHERE user_id = %s {all_or_something}
        ORDER BY scheduled_date, scheduled_time DESC
        LIMIT %s
        OFFSET %s;
    """

    with database_access as (conn, cursor):
        # Update missed workouts before retrieving the schedule
        await utils.update_missed_workouts(user_id=user_id, conn=conn, cursor=cursor)

        # Prepare parameters based on the status filter
        params = (
            (user_id, workout_status, limit, skip)
            if workout_status != "all"
            else (user_id, limit, skip)
        )

        try:
            # Execute the query to get the scheduled workouts
            cursor.execute(workout_schedule_query, params)
            workout_schedule_out = cursor.fetchall()
        except Exception as error:
            logger.error(
                f"Error occurred while trying to retrieve workout schedules: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        # Fetch and attach plan details for each scheduled workout
        for x, schedule in enumerate(workout_schedule_out):
            plan_details = await fetch_plan_with_exercises(
                schedule["plan_id"], user_id, cursor
            )
            workout_schedule_out[x].update({"plan_details": plan_details})

        if not workout_schedule_out:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Schedule Not Found"
            )

        return workout_schedule_out


@router.get(
    "/scheduled-workouts/{scheduled_workout_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a scheduled workout.",
    response_model=scheduled_workouts_schemas.ScheduledWorkoutOut,
    description=docs.get_workout_schedule,
)
async def get_workout_schedule(
    scheduled_workout_id: str,
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):

    user_id = current_user.user_id

    # SQL query to retrieve a specific scheduled workout by its ID
    workout_schedule_query = f"""
        SELECT *
        FROM scheduled_workouts
        WHERE user_id = %s AND scheduled_workout_id = %s
        ORDER BY scheduled_date, scheduled_time
    """

    with database_access as (conn, cursor):
        # Update missed workouts before retrieving the specific schedule
        await utils.update_missed_workouts(user_id, conn, cursor)

        try:
            # Execute the query to get the specific scheduled workout
            cursor.execute(workout_schedule_query, (user_id, scheduled_workout_id))
            workout_schedule_out = cursor.fetchone()
        except Exception as error:
            logger.error(
                f"Error occurred while getting a specific workout schedule: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        if not workout_schedule_out:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Schedule Not Found"
            )

        # Fetch and attach plan details to the workout schedule
        plan_details = await fetch_plan_with_exercises(
            workout_schedule_out["plan_id"], user_id, cursor
        )
        workout_schedule_out.update({"plan_details": plan_details})

        return workout_schedule_out


@router.patch(
    "/scheduled-workouts/{scheduled_workout_id}",
    status_code=status.HTTP_200_OK,
    summary="Update a scheduled workout",
    response_model=scheduled_workouts_schemas.ScheduledWorkoutOut,
    description=docs.update_workout_schedule,
)
async def update_workout_plan(
    scheduled_workout_id: str,
    scheduled_workout_update: Annotated[scheduled_workouts_schemas.ScheduledWorkoutUpdate,Body(openapi_examples=examples.workout_schedule_examples)],
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):

    user_id = current_user.user_id

    plan_id_check_query = sql.SQL(
        """
                        SELECT plan_id
                        FROM workout_plans
                        WHERE user_id = %s AND plan_id = %s
                    """
    )

    with database_access as (conn, cursor):
        if scheduled_workout_update.plan_id:

            try:
                cursor.execute(
                    plan_id_check_query, (user_id, scheduled_workout_update.plan_id)
                )
                plan_id_verification = cursor.fetchone()
            except Exception as error:
                logger.error(
                    f"Error occurred while checking plan_id: {str(error)}",
                    exc_info=True,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
                )

            if not plan_id_verification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workout Plan Not found",
                )

        await utils.update_missed_workouts(user_id, conn, cursor)
        updated_data = scheduled_workout_update.model_dump(exclude_unset=True)

        update_plan_query = """ UPDATE scheduled_workouts SET """

        for key in updated_data.keys():
            update_plan_query += f" {key} = %s, "

        update_plan_query = update_plan_query[0 : len(update_plan_query) - 2]
        update_plan_query += " WHERE scheduled_workout_id = %s AND user_id = %s "
        update_plan_query += " RETURNING *"

        params = list(updated_data.values())
        params.extend([scheduled_workout_id, user_id])

        try:
            cursor.execute(update_plan_query, params)
        except Exception as error:
            logger.error(
                f"An error occurred while updating the workout_schedules: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        updated_workout_schedule = cursor.fetchone()

        plan_details = await fetch_plan_with_exercises(
            updated_workout_schedule["plan_id"], user_id, cursor
        )
        updated_workout_schedule.update({"plan_details": plan_details})

        conn.commit()

        return updated_workout_schedule


@router.delete(
    "/scheduled-workouts/{scheduled_workout_id}",
    status_code=status.HTTP_200_OK,
    summary="Cancel a scheduled workout",
    description=docs.delete_workout_schedule
)
async def delete_scheduled_workout(
    scheduled_workout_id: str,
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):
    user_id = current_user.user_id

    delete_workout_query = """
            DELETE FROM scheduled_workouts
            WHERE scheduled_workout_id = %s AND user_id = %s
            RETURNING *;
            """
    with database_access as (conn, cursor):

        try:
            cursor.execute(delete_workout_query, (scheduled_workout_id, user_id))
            deleted_schedule = cursor.fetchone()
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error deleting scheduled workout: {str(error)}",
            )

        if not deleted_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout Schedule not found",
            )

        conn.commit()

        return {"message": "Scheduled workout deleted successfully."}
