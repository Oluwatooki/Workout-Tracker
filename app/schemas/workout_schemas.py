import datetime
from uuid import UUID

from pydantic import BaseModel


class ExercisePlanIn(BaseModel):
    exercise_id: int
    sets: int
    reps: int
    weight: float = None


class WorkoutPlanCreate(BaseModel):
    name: str
    description: str = None
    exercises: list[ExercisePlanIn]


class ExercisePlanOut(BaseModel):
    plan_exercise_id: UUID
    plan_id: UUID
    exercise_id: int
    sets: int
    reps: int
    weight: float = None


class WorkoutPlanOut(BaseModel):
    plan_id: UUID
    user_id: UUID
    name: str
    description: str = None
    created_at: datetime.datetime
    exercises: list[ExercisePlanOut]
