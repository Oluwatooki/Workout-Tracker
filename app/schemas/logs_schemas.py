import datetime
from uuid import UUID
from pydantic import BaseModel


class WorkoutLogBase(BaseModel):
    completed_at: datetime.datetime
    total_time: int
    notes: str


class WorkoutLogCreate(WorkoutLogBase):
    scheduled_workout_id: str
    pass


class WorkoutLogOut(WorkoutLogBase):
    scheduled_workout_id: str | None
    log_id: UUID
    user_id: UUID
