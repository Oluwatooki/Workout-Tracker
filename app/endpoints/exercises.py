import logging
from fastapi import HTTPException, status, APIRouter, Depends, Path
from app.schemas import exercises_schemas
from app.db import connection
from app.core import docs
from app.db.seeds.seed_exercises import num_exercises
from psycopg2 import sql

# Create an APIRouter and setup logging
router = APIRouter(tags=["Exercises"])
logger = logging.getLogger(__name__)


@router.get(
    "/exercises",
    status_code=status.HTTP_200_OK,
    summary="Retrieves all exercises",
    response_model=list[exercises_schemas.ExerciseModel],
    description=docs.get_exercises,
)
async def get_exercises(database_access: list = Depends(connection.get_db)):
    with database_access as (conn, cursor):
        try:
            # Fetches all exercises and return them
            insert_query = sql.SQL(""" SELECT * FROM exercises """)
            cursor.execute(insert_query)
            exercises = cursor.fetchall()
            return exercises
        except Exception as error:
            # Log error and raise HTTP exception if something goes wrong
            logger.exception(str(error))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )


@router.get(
    "/exercises/{exercise_id}",
    status_code=status.HTTP_200_OK,  # Status code 200 OK for successful retrieval
    summary="Retrieves a particular exercise",
    response_model=exercises_schemas.ExerciseModel,
    description=docs.get_exercise_by_id
)
async def get_exercise(
    exercise_id: int = Path(
        ..., description="The ID of the exercise to retrieve", ge=1, le=num_exercises
    ),
    database_access: list = Depends(connection.get_db),
):
    with database_access as (conn, cursor):
        try:
            # Fetches and retrieves a specific exercise using the id
            select_query = sql.SQL("""SELECT * FROM exercises WHERE exercise_id = %s""")
            cursor.execute(select_query, (exercise_id,))
            exercise = cursor.fetchone()
        except Exception as error:
            # Log error and raise HTTP exception if something goes wrong
            logger.error(f"Error retrieving exercise: {error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )
        else:
            if exercise:
                # Return the exercise details if found
                logger.info(f"Exercise retrieved: {exercise}")
                return exercise
            else:
                # Raise HTTP 404 if exercise not found
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No Exercise with that ID",
                )
