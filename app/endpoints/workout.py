import logging
from typing import Annotated
import psycopg2
from fastapi import HTTPException, status, APIRouter, Depends, Body, Path
from app.core.utils import fetch_plan_with_exercises
from app.schemas import users_schemas, workout_schemas
from app.db import connection
from app.core import security, docs, examples
from psycopg2 import sql

router = APIRouter(tags=["Workout Management"])
logger = logging.getLogger(__name__)


@router.post(
    "/workout-plans",
    status_code=status.HTTP_201_CREATED,
    summary="Creating a new workout Plan",
    response_model=workout_schemas.WorkoutPlanOut,
    description=docs.create_workout_plan,
)
async def create_workout_plan(
    workout_plan: Annotated[
        workout_schemas.WorkoutPlanCreate,
        Body(openapi_examples=examples.workout_examples),
    ],
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):
    user_id = current_user.user_id  # Extract user ID from token data

    # SQL query to insert a new workout plan
    insert_plan_query = sql.SQL(
        """
        INSERT INTO workout_plans (user_id, name, description)
        VALUES (%s, %s, %s)
        RETURNING plan_id, user_id, name AS plan_name, description,created_at,updated_at;
        """
    )

    # SQL query to insert exercises into the workout_plan_exercises table
    insert_exercise_query = sql.SQL(
        """
        INSERT INTO workout_plan_exercises (plan_id, exercise_id, sets, reps, weight,comments)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING plan_exercise_id, exercise_id, sets, reps, weight,comments;
        """
    )

    # SQL query to retrieve exercise details by exercise ID
    select_query = sql.SQL(
        """SELECT name AS exercise_name,description,
                              category FROM exercises WHERE exercise_id = %s"""
    )

    with database_access as (conn, cursor):

        try:
            # Insert the workout plan and retrieve the inserted plan
            cursor.execute(
                insert_plan_query,
                (user_id, workout_plan.plan_name, workout_plan.description),
            )
            plan = cursor.fetchone()
        except Exception as error:
            logger.error(
                f"An error occurred while inserting workout plan: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        plan_id = plan["plan_id"]
        exercises_out = []

        try:
            for exercise in workout_plan.exercises:
                # Insert each exercise into the workout plan and retrieve tit
                cursor.execute(
                    insert_exercise_query,
                    (
                        plan_id,
                        exercise.exercise_id,
                        exercise.sets,
                        exercise.reps,
                        exercise.weight,
                        exercise.comments,
                    ),
                )
                exercise_data = cursor.fetchone()

                if exercise_data:
                    # Fetch additional exercise info from the exercises table
                    cursor.execute(select_query, (exercise.exercise_id,))
                    exercise_extra_info = dict(cursor.fetchone())

                    exercise_data = dict(exercise_data)
                    exercise_data.update(**exercise_extra_info)

                    # Append the exercise data to the output list
                    exercises_out.append(
                        workout_schemas.ExercisePlanOut(**exercise_data)
                    )
                else:
                    logger.warning(
                        f"Exercise data retrieval returned no results for exercise: {exercise.exercise_id}"
                    )
        except psycopg2.errors.ForeignKeyViolation as error:
            # Handle error where the exercise ID does not exist
            logger.error(f"Foreign key violation: {str(error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Exercise id {exercise.exercise_id} does not exist",
            )
        except Exception as error:
            # Handle other exceptions
            logger.error(
                f"An error occurred while inserting exercises: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        # Combine the plan data with the associated exercises
        plan = dict(plan)
        plan.update({"exercises": exercises_out})

        conn.commit()

        return workout_schemas.WorkoutPlanOut(**plan)  # Return the final workout plan

    # The function first inserts a new workout plan (check workout_schemas.WorkoutPlanCreate)
    # into the workout_plans table and retrieves details
    # like plan_id, user_id, name, description,and created_at from the inserted record.
    # It then processes each exercise from the workout plan(check workout_schemas.WorkoutPlanCreate),
    # executing SQL queries to add them to the workout_plan_exercises table.
    # After completing these operations,
    # the function saves this information to the database, and returns the created workout plan
    # along with its associated exercises


@router.put(
    "/workout-plans/{plan_id}",
    status_code=status.HTTP_200_OK,  # Status code indicating successful update
    summary="Update a workout plan",
    response_model=workout_schemas.WorkoutPlanOut,
    description=docs.update_workout_plan,
)
async def update_workout_plan(
    plan_id: Annotated[str, Path()],
    workout_plan: Annotated[
        workout_schemas.WorkoutPlanCreate,
        Body(openapi_examples=examples.workout_examples),
    ],
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):
    user_id = current_user.user_id  # Extract user ID from token data

    # SQL query to update the workout plan's name and description
    update_plan_query = sql.SQL(
        """
        UPDATE workout_plans
        SET name = %s, description = %s
        WHERE plan_id = %s AND user_id = %s
        RETURNING plan_id, user_id, name AS plan_name, description, created_at, updated_at;
        """
    )

    # SQL query to delete all exercises associated with the workout plan from workout_plan_exercises
    delete_exercises_query = sql.SQL(
        """DELETE FROM workout_plan_exercises WHERE plan_id = %s"""
    )

    # SQL query to insert exercises into the workout_plan_exercises table
    insert_exercise_query = sql.SQL(
        """
        INSERT INTO workout_plan_exercises (plan_id, exercise_id, sets, reps, weight, comments)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING plan_exercise_id, plan_id, exercise_id, sets, reps, weight, comments;
        """
    )

    with database_access as (conn, cursor):
        try:
            # Update the workout plan's details
            cursor.execute(
                update_plan_query,
                (
                    workout_plan.plan_name,
                    workout_plan.description,
                    plan_id,
                    user_id,
                ),
            )
            updated_plan = cursor.fetchone()  # Retrieve the updated plan
            # If the updated_plan is None, Then return a 404 error
            if not updated_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workout plan not found or not owned by user",
                )

            # Delete existing exercises for the plan
            cursor.execute(delete_exercises_query, (plan_id,))

        except Exception as error:
            logger.error(
                f"An error occurred while updating the workout plan: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        exercises_out = []
        try:
            for exercise in workout_plan.exercises:
                # Insert each exercise into the updated workout plan
                cursor.execute(
                    insert_exercise_query,
                    (
                        plan_id,
                        exercise.exercise_id,
                        exercise.sets,
                        exercise.reps,
                        exercise.weight,
                        exercise.comments,
                    ),
                )
                exercise_data = dict(cursor.fetchone())

                # Retrieve additional exercise details
                select_query = sql.SQL(
                    """SELECT name AS exercise_name, description, category
                    FROM exercises WHERE exercise_id = %s"""
                )
                cursor.execute(select_query, (exercise.exercise_id,))

                exercise_extra_info = dict(cursor.fetchone())
                exercise_data.update(**exercise_extra_info)

                # Append the exercise data to the output list
                exercises_out.append(workout_schemas.ExercisePlanOut(**exercise_data))
        except psycopg2.errors.ForeignKeyViolation as error:
            # Handle cases where the exercise ID does not exist
            logger.error(
                f"An error occurred while updating the workout plan: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Exercise id {exercise.exercise_id} does not exist",
            )
        except Exception as error:
            # Handle other exceptions
            logger.error(
                f"An error occurred while updating the workout plan: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        # Combine the updated plan data with the associated exercises
        updated_plan = dict(updated_plan)
        updated_plan.update({"exercises": exercises_out})

        conn.commit()

        return workout_schemas.WorkoutPlanOut(
            **updated_plan
        )  # Return the updated workout plan


@router.get(
    "/workout-plans",
    status_code=status.HTTP_200_OK,
    summary="List all workout plans for the current user",
    response_model=list[workout_schemas.WorkoutPlanOutV2],
    description=docs.list_workout_plans,
)
async def list_workout_plans(
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
    limit: int = 10,
    skip: int = 0,
):
    user_id = current_user.user_id

    # SQL query to select workout plans for the current user and adjust it using limit and offset
    select_plans_query = sql.SQL(
        """
        SELECT plan_id, user_id, name AS plan_name, description, created_at, updated_at
        FROM workout_plans
        WHERE user_id = %s
        LIMIT %s
        OFFSET %s;
        """
    )

    # SQL query to select exercises associated with a specific workout plan from the workout_plan_exercises table
    select_plans_exercises_query = sql.SQL(
        """
        SELECT *
        FROM workout_plan_exercises
        WHERE plan_id = %s;
        """
    )

    # SQL query to select additional exercise details
    select_exercises_query = sql.SQL(
        """SELECT name AS exercise_name, description, category 
        FROM exercises WHERE exercise_id = %s"""
    )

    with database_access as (conn, cursor):
        try:
            # Retrieve the workout plans for the current user
            cursor.execute(select_plans_query, (user_id, limit, skip))
            plans = cursor.fetchall()
        except Exception as error:
            logger.error(
                f"Error occurred while getting a list of all workout plans: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )
        # If there are no workout return a 404 error
        if not plans:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No workout plans found for the user.",
            )

        try:
            for i, plan in enumerate(plans):
                # Retrieve exercises associated with each workout plan
                cursor.execute(select_plans_exercises_query, (plan["plan_id"],))
                exercises = cursor.fetchall()

                for x, exercise in enumerate(exercises):
                    # Retrieve additional exercise details
                    cursor.execute(select_exercises_query, (exercise["exercise_id"],))
                    exercise_data = dict(cursor.fetchone())

                    exercises[x].update(
                        **exercise_data
                    )  # Update exercise data with extra details

                plans[i].update({"exercises": exercises})  # Add exercises to the plan
                plans[i].update(
                    {"metadata": {"exercise_count": len(exercises)}}
                )  # Add metadata to the plan

        except Exception as error:
            logger.error(
                f"Error occurred while getting a specific workout plan: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        return plans  # Return the list of workout plans


@router.get(
    "/workout-plans/{plan_id}",
    status_code=status.HTTP_200_OK,
    summary="List a specific workout plan for the current user",
    response_model=workout_schemas.WorkoutPlanOutV2,
    description=docs.get_workout_plan,
)
async def get_workout_plan(
    plan_id: Annotated[str,Path()],
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):

    user_id = current_user.user_id

    with database_access as (conn, cursor):
        plan = await fetch_plan_with_exercises(plan_id, user_id, cursor)

        return plan


@router.delete(
    "/workout-plans/{plan_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a workout plan",
    description=docs.delete_workout_plan,
)
async def delete_workout_plan(
    plan_id: Annotated[str,Path()],
    database_access: list = Depends(connection.get_db),
    current_user: users_schemas.TokenData = Depends(security.get_current_user),
):
    user_id = current_user.user_id  # Extract user ID from token data

    # SQL query to delete a workout plan if it belongs to the current user
    delete_plan_query = sql.SQL(
        """
            DELETE FROM workout_plans
            WHERE plan_id = %s AND user_id = %s
            RETURNING plan_id;
        """
    )

    with database_access as (conn, cursor):
        try:
            # Execute the delete query
            cursor.execute(delete_plan_query, (plan_id, user_id))
            deleted_plan = cursor.fetchone()
        except Exception as error:
            logger.error(
                f"An error occurred while deleting the workout plan: {str(error)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )

        if not deleted_plan:
            # Raise an error if the plan wasn't found or the user doesn't have permission
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout plan not found or you do not have permission to delete it",
            )

        conn.commit()

        return {"message": "Workout plan deleted successfully"}  # Confirm deletion
