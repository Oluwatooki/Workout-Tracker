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

    # Insert exercises into workout plan
    insert_exercise_query = sql.SQL("""
        INSERT INTO workout_plan_exercises (plan_id, exercise_id, sets, reps, weight)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING plan_exercise_id, plan_id, exercise_id, sets, reps, weight;
    """)
    try:
        for exercise in workout_plan.exercises:
            cursor.execute(insert_exercise_query, (
                plan_id,
                exercise.exercise_id,
                exercise.sets,
                exercise.reps,
                exercise.weight
            ))
            exercise_data = cursor.fetchone()
            if exercise_data:  # Ensure data is valid
                exercise_entry = workout_schemas.ExercisePlanOut(**{
                    'plan_exercise_id': exercise_data['plan_exercise_id'],
                    'plan_id': exercise_data['plan_id'],
                    'exercise_id': exercise_data['exercise_id'],
                    'sets': exercise_data['sets'],
                    'reps': exercise_data['reps'],
                    'weight': float(exercise_data['weight']) if exercise_data['weight'] else None
                })
                exercises_out.append(exercise_entry)
            else:
                logger.warning(f"Exercise data retrieval returned no results for exercise: {exercise.exercise_id}")
    except psycopg2.errors.ForeignKeyViolation as error:
        logger.error(f"Foreign key violation: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Exercise id {exercise.exercise_id} does not exist')
    except Exception as error:
        logger.error(f"An error occurred while inserting exercises: {str(error)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    # Commit transaction and close connection
    conn.commit()
    cursor.close()
    conn.close()

    # Return the created workout plan with exercises
    return workout_schemas.WorkoutPlanOut(
        plan_id=plan['plan_id'],
        user_id=plan['user_id'],
        name=plan['name'],
        description=plan['description'],
        created_at=plan['created_at'],
        exercises=exercises_out,
    )

    # The function first inserts a new workout plan (check workout_schemas.WorkoutPlanCreate)
    # into the workout_plans table and retrieves details
    # such as plan_id, user_id, name, description,and created_at from the inserted record.
    # It then processes each exercise from the workout plan(check workout_schemas.WorkoutPlanCreate),
    # executing SQL queries to add them to the workout_plan_exercises table.
    # After completing these operations,
    # the function saves this information to the database, and returns the newly created workout plan
    # along with its associated exercises.
