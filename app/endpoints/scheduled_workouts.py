import logging
import psycopg2
from fastapi import HTTPException, status, APIRouter, Depends, Request, Query

from app.core.utils import fetch_plan_with_exercises
from app.schemas import users_schemas, scheduled_workouts_schemas
from app.db import connection
from app.core import security, utils
from psycopg2 import sql

router = APIRouter(tags=['Scheduled Workout Management'])
logger = logging.getLogger(__name__)


@router.post(
    "/scheduled-workouts",
    status_code=status.HTTP_201_CREATED,
    summary='Schedule a workout.',
    response_model=scheduled_workouts_schemas.ScheduledWorkoutOut
)
async def create_workout_schedule(
        scheduled_workout: scheduled_workouts_schemas.ScheduledWorkoutCreate,
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id

    plan_id_check_query = sql.SQL("""
        SELECT plan_id
        FROM workout_plans
        WHERE user_id = %s AND plan_id = %s
    """)
    try:
        cursor.execute(plan_id_check_query, (user_id, scheduled_workout.plan_id))
        plan_id_verification = cursor.fetchone()
    except Exception as error:
        logger.error(f"Error occurred while checking plan_id: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    if not plan_id_verification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Workout Plan Not found')

    insert_schedule_query = sql.SQL("""
        INSERT INTO scheduled_workouts (plan_id, user_id, scheduled_date, scheduled_time, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *;
    """)
    try:
        cursor.execute(insert_schedule_query, (scheduled_workout.plan_id, user_id, scheduled_workout.scheduled_date,
                                               scheduled_workout.scheduled_time, scheduled_workout.status))
        workout_schedule_out = cursor.fetchone()
    except Exception as error:
        logger.error(f"Error occurred while scheduling the workout: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    plan_details = await fetch_plan_with_exercises(scheduled_workout.plan_id, user_id, cursor)
    workout_schedule_out.update({'plan_details': plan_details})
    conn.commit()
    cursor.close()
    conn.close()

    return workout_schedule_out


@router.get(
    "/scheduled-workouts",
    status_code=status.HTTP_201_CREATED,
    summary='Get a list of scheduled workouts.',
    response_model=list[scheduled_workouts_schemas.ScheduledWorkoutOut],
)
async def get_workout_schedule(
        workout_status: scheduled_workouts_schemas.StatusChoice,
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id

    await utils.update_missed_workouts(user_id=user_id, database_access=database_access)

    all_or_something = 'AND status = %s' if workout_status != 'all' else ' '
    workout_schedule_query = f"""
            SELECT *
            FROM scheduled_workouts
            WHERE user_id = %s {all_or_something}
            ORDER BY scheduled_date,scheduled_time DESC
        """

    params = (user_id, workout_status) if workout_status != 'all' else (user_id,)
    try:
        cursor.execute(workout_schedule_query, params)
        workout_schedule_out = cursor.fetchall()
    except Exception as error:
        logger.error(f"Error occurred while trying to retrieve workout schedules: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
    for x,schedule in enumerate(workout_schedule_out):

        plan_details = await fetch_plan_with_exercises(schedule['plan_id'], user_id, cursor)
        workout_schedule_out[x].update({'plan_details': plan_details})

    cursor.close()
    conn.close()
    return workout_schedule_out


@router.get(
    "/scheduled-workouts/{scheduled_workout_id}",
    status_code=status.HTTP_201_CREATED,
    summary='Get a scheduled workout.',
    response_model=scheduled_workouts_schemas.ScheduledWorkoutOut,
)
async def get_workout_schedule(
        schedule_workout_id: str,
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id
    await utils.update_missed_workouts(user_id, database_access=database_access)

    workout_schedule_query = f"""
                SELECT *
                FROM scheduled_workouts
                WHERE user_id = %s AND scheduled_workout_id = %s
                ORDER BY scheduled_date,scheduled_time
            """

    try:
        cursor.execute(workout_schedule_query, (user_id, schedule_workout_id))
        workout_schedule_out = cursor.fetchone()
    except Exception as error:
        logger.error(f"Error occurred while getting a specific workout schedule: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
    if not workout_schedule_out:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Schedule Not found')

    plan_details = await fetch_plan_with_exercises(workout_schedule_out['plan_id'], user_id, cursor)
    workout_schedule_out.update({'plan_details': plan_details})
    cursor.close()
    conn.close()
    return workout_schedule_out


@router.patch(
    "/scheduled-workouts/{scheduled_workout_id}",
    status_code=status.HTTP_200_OK,
    summary='Update a workout plan',
    response_model=scheduled_workouts_schemas.ScheduledWorkoutOut
)
async def update_workout_plan(
        scheduled_workout_id: str,
        scheduled_workout_update: scheduled_workouts_schemas.ScheduledWorkoutUpdate,
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id

    if scheduled_workout_update.plan_id:
        plan_id_check_query = sql.SQL("""
                SELECT plan_id
                FROM workout_plans
                WHERE user_id = %s AND plan_id = %s
            """)
        try:
            cursor.execute(plan_id_check_query, (user_id, scheduled_workout_update.plan_id))
            plan_id_verification = cursor.fetchone()
        except Exception as error:
            logger.error(f"Error occurred while checking plan_id: {str(error)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

        if not plan_id_verification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Workout Plan Not found')

    await utils.update_missed_workouts(user_id, database_access=database_access)
    updated_data = scheduled_workout_update.model_dump(exclude_unset=True)

    update_plan_query = """ UPDATE scheduled_workouts SET """
    for key in updated_data.keys():
        update_plan_query += f' {key} = %s, '
    update_plan_query = update_plan_query[0:len(update_plan_query) - 2]

    update_plan_query += ' WHERE scheduled_workout_id = %s AND user_id = %s '
    update_plan_query += ' RETURNING *'
    params = list(updated_data.values())
    params.extend([scheduled_workout_id, user_id])
    try:
        cursor.execute(update_plan_query, params)
    except Exception as error:
        logger.error(f"An error occurred while updating the workout_schedules: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
    updated_workout_schedule = cursor.fetchone()

    plan_details = await fetch_plan_with_exercises(updated_workout_schedule['plan_id'], user_id, cursor)
    updated_workout_schedule.update({'plan_details': plan_details})

    conn.commit()
    cursor.close()
    conn.close()
    return updated_workout_schedule


@router.delete(
    "/scheduled-workouts/{scheduled_workout_id}",
    status_code=status.HTTP_200_OK,
    summary='Delete a scheduled workout.',
)
async def delete_scheduled_workout(
        scheduled_workout_id: str,
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id

    delete_workout_query = """
    DELETE FROM scheduled_workouts
    WHERE scheduled_workout_id = %s AND user_id = %s
    RETURNING *;
    """
    try:
        cursor.execute(delete_workout_query, (scheduled_workout_id, user_id))
        deleted_schedule = cursor.fetchone()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error deleting scheduled workout: {str(error)}")
    if not deleted_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout Schedule not found"
        )
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Scheduled workout deleted successfully."}
