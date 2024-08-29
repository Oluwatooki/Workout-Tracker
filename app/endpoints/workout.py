import logging
import psycopg2
from fastapi import HTTPException, status, APIRouter, Depends, Request, Query
from app.schemas import users_schemas, workout_schemas
from app.db import connection
from app.core import security
from psycopg2 import sql

router = APIRouter(tags=['Workout Management'])
logger = logging.getLogger(__name__)


@router.post(
    "/workout-plans",
    status_code=status.HTTP_201_CREATED,
    summary='Creating a new workout Plan',
    response_model=workout_schemas.WorkoutPlanOut,
)
async def create_workout_plan(
        workout_plan: workout_schemas.WorkoutPlanCreate,
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id

    # Insert workout plan
    insert_plan_query = sql.SQL("""
        INSERT INTO workout_plans (user_id, name, description)
        VALUES (%s, %s, %s)
        RETURNING plan_id, user_id, name, description,created_at;
    """)
    try:
        cursor.execute(insert_plan_query, (user_id, workout_plan.name, workout_plan.description))
        plan = cursor.fetchone()
    except Exception as error:
        logger.error(f"An error occurred while inserting workout plan: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    plan_id = plan['plan_id']
    exercises_out = []

    insert_exercise_query = sql.SQL("""
        INSERT INTO workout_plan_exercises (plan_id, exercise_id, sets, reps, weight,comments)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING plan_exercise_id, plan_id, exercise_id, sets, reps, weight,comments;
    """)
    try:
        for exercise in workout_plan.exercises:
            cursor.execute(insert_exercise_query, (
                plan_id, exercise.exercise_id, exercise.sets, exercise.reps, exercise.weight, exercise.comments
            ))
            exercise_data = cursor.fetchone()
            if exercise_data:
                exercises_out.append(exercise_data)
            else:
                logger.warning(f"Exercise data retrieval returned no results for exercise: {exercise.exercise_id}")
    except psycopg2.errors.ForeignKeyViolation as error:
        logger.error(f"Foreign key violation: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Exercise id {exercise.exercise_id} does not exist')
    except Exception as error:
        logger.error(f"An error occurred while inserting exercises: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    conn.commit()
    cursor.close()
    conn.close()

    plan = dict(plan)
    plan.update({'exercises': exercises_out})

    return workout_schemas.WorkoutPlanOut(**plan)

    # The function first inserts a new workout plan (check workout_schemas.WorkoutPlanCreate)
    # into the workout_plans table and retrieves details
    # such as plan_id, user_id, name, description,and created_at from the inserted record.
    # It then processes each exercise from the workout plan(check workout_schemas.WorkoutPlanCreate),
    # executing SQL queries to add them to the workout_plan_exercises table.
    # After completing these operations,
    # the function saves this information to the database, and returns the newly created workout plan
    # along with its associated exercises
    #


@router.delete(
    "/workout-plans/{plan_id}",
    status_code=status.HTTP_200_OK,
    summary='Delete a workout plan',
)
async def delete_workout_plan(
        plan_id: str,
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id

    # Check if the workout plan exists and belongs to the current user
    select_plan_query = sql.SQL("""
        SELECT * FROM workout_plans
        WHERE plan_id = %s AND user_id = %s
    """)

    cursor.execute(select_plan_query, (plan_id, user_id))
    plan = cursor.fetchone()

    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Workout plan not found or you do not have permission to modify it")

    delete_plan_query = sql.SQL("""
            DELETE FROM workout_plans
            WHERE plan_id = %s AND user_id = %s
            RETURNING *
        """)

    cursor.execute(delete_plan_query, (plan_id, user_id))
    deleted = cursor.fetchall()
    conn.commit()
    return deleted


@router.put(
    "/workout-plans/{plan_id}",
    status_code=status.HTTP_200_OK,
    summary='Update a workout plan',
    response_model=workout_schemas.WorkoutPlanOut
)
async def update_workout_plan(
        plan_id: str,
        workout_plan: workout_schemas.WorkoutPlanCreate,
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id

    # Update workout plan details
    update_plan_query = sql.SQL("""
        UPDATE workout_plans
        SET name = %s, description = %s
        WHERE plan_id = %s AND user_id = %s
        RETURNING plan_id, user_id, name, description, created_at;
    """)
    try:
        cursor.execute(update_plan_query, (workout_plan.name, workout_plan.description, plan_id, user_id))
        updated_plan = cursor.fetchone()
        if not updated_plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Workout plan not found or not owned by user")

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    delete_exercises_query = sql.SQL("""
        DELETE FROM workout_plan_exercises WHERE plan_id = %s
    """)
    cursor.execute(delete_exercises_query, (plan_id,))

    insert_exercise_query = sql.SQL("""
        INSERT INTO workout_plan_exercises (plan_id, exercise_id, sets, reps, weight, comments)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING plan_exercise_id, plan_id, exercise_id, sets, reps, weight, comments;
    """)
    exercises_out = []
    try:
        for exercise in workout_plan.exercises:
            cursor.execute(insert_exercise_query, (plan_id, exercise.exercise_id, exercise.sets,
                                                   exercise.reps, exercise.weight, exercise.comments
                                                   ))
            exercise_data = cursor.fetchone()
            exercises_out.append(exercise_data)
    except psycopg2.errors.ForeignKeyViolation as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Exercise id {exercise.exercise_id} does not exist')
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    conn.commit()
    cursor.close()
    conn.close()

    updated_plan = dict(updated_plan)
    updated_plan.update({'exercises': exercises_out})

    return workout_schemas.WorkoutPlanOut(**updated_plan)


@router.get(
    "/workout-plans",
    status_code=status.HTTP_200_OK,
    summary="List all workout plans for the current user",
    # response_model=list[workout_schemas.WorkoutPlanOut]
)
async def list_workout_plans(
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id

    select_plans_query = sql.SQL("""
        SELECT plan_id, user_id, name, description, created_at, updated_at
        FROM workout_plans
        WHERE user_id = %s;
    """)
    try:
        cursor.execute(select_plans_query, (user_id,))
        plans = cursor.fetchall()
    except Exception as error:
        logger.error(f"Error occurred: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    if not plans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No workout plans found for the user."
        )
    for i, plan in enumerate(plans):
        select_plans_exercises_query = sql.SQL("""
            SELECT *
            FROM workout_plan_exercises
            WHERE plan_id = %s;
        """)

        cursor.execute(select_plans_exercises_query, (plan['plan_id'],))
        exercises = cursor.fetchall()
        plans[i].update({'exercises': exercises})
        plans[i].update({'metadata': {'exercise_count': len(exercises)}})

    return plans


@router.get(
    "/workout-plans/{plan_id}",
    status_code=status.HTTP_200_OK,
    summary="List a specific workout plan for the current user",
    # response_model=list[workout_schemas.WorkoutPlanOut]
)
async def get_workout_plan(
        plan_id: str,
        database_access: list = Depends(connection.get_db),
        current_user: users_schemas.TokenData = Depends(security.get_current_user)
):
    conn, cursor = database_access
    user_id = current_user.user_id

    select_plan_query = sql.SQL("""
        SELECT plan_id, user_id, name, description, created_at, updated_at
        FROM workout_plans
        WHERE user_id = %s AND plan_id = %s;
    """)
    try:
        cursor.execute(select_plan_query, (user_id, plan_id,))
        plan = cursor.fetchone()
    except Exception as error:
        logger.error(f"Error occurred: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No workout plans found for the user."
        )

    select_plan_exercises_query = sql.SQL("""
        SELECT *
        FROM workout_plan_exercises
        WHERE plan_id = %s;
    """)
    try:
        cursor.execute(select_plan_exercises_query, (plan['plan_id'],))
        exercises = cursor.fetchall()
        plan.update({'exercises': exercises})
        plan.update({'metadata': {'exercise_count': len(exercises)}})
    except Exception as error:
        logger.error(f"Error occurred: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    return plan
