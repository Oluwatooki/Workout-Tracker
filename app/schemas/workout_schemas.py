import datetime
from uuid import UUID
from fastapi import Body
from pydantic import BaseModel, Field


class ExercisePlanBase(BaseModel):
    exercise_id: int = Field(..., example=4)
    sets: int = Field(..., ge=0, example=10)
    reps: int = Field(..., ge=0, example=6)
    weight: float | int | None = Field(
        None,ge=0,example=20
    )
    comments: str | None = Field(None,example='This may be strenuous')


class ExercisePlanCreate(ExercisePlanBase):
    pass


class ExercisePlanOut(ExercisePlanBase):
    exercise_name: str = Field(...,example='Plank')
    description: str = Field(..., example='A basic plank')
    category: str = Field(...,example='flexibility')


class WorkoutPlanBase(BaseModel):
    plan_name: str = Field(..., example="Full Body Workout")
    description: str | None = Field(
        None, example="This Workout focuses on your entire body"
    )


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
    metadata: dict = Field(...,example={'exercise_count':1})


class WorkoutPlanOutV3(BaseModel):
    plan_name: str = Field(...,example='Full Body workout')
    description: str | None = Field(None,example='This involves your entire body')
    created_at: datetime.datetime
    updated_at: datetime.datetime
    exercises: list[ExercisePlanOut]


class WorkoutPlanUpdate(BaseModel):
    plan_name: str
    description: str
    exercises: list[ExercisePlanCreate]
