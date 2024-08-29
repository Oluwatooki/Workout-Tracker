import datetime
from uuid import UUID

from pydantic import BaseModel


class ExercisePlanBase(BaseModel):
    exercise_id: int
    sets: int
    reps: int
    weight: float | int | None = None
    comments: str | None = None


class ExercisePlanCreate(ExercisePlanBase):
    pass


class ExercisePlanOut(ExercisePlanBase):
    plan_exercise_id: UUID


class WorkoutPlanBase(BaseModel):
    name: str
    description: str | None = None


class WorkoutPlanCreate(WorkoutPlanBase):
    exercises: list[ExercisePlanCreate]


class WorkoutPlanOut(WorkoutPlanBase):
    plan_id: UUID
    user_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    exercises: list[ExercisePlanOut]


class WorkoutPlanOutV2(WorkoutPlanBase):
    plan_id: UUID
    user_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    exercises: list[ExercisePlanOut]
    metadata: dict


class WorkoutPlanUpdate(BaseModel):
    name: str
    description: str
    exercises: list[ExercisePlanCreate]
