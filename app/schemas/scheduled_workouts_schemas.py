import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel


class StatusEnum(str, Enum):
    pending = 'pending'
    completed = 'completed'
    missed = 'missed'


class StatusChoice(str, Enum):
    pending = 'pending'
    completed = 'completed'
    missed = 'missed'
    all = 'all'


class ScheduledWorkoutBase(BaseModel):
    plan_id: str
    scheduled_date: datetime.date
    scheduled_time: datetime.time
    status: StatusEnum = StatusEnum.pending


class ScheduledWorkoutCreate(ScheduledWorkoutBase):
    pass


class ScheduledWorkoutUpdate(BaseModel):
    plan_id: str | None = None
    scheduled_date: datetime.date | None = None
    scheduled_time: datetime.time | None = None
    status: StatusEnum | None = None


class ScheduledWorkoutOut(ScheduledWorkoutBase):
    scheduled_workout_id: UUID
    user_id: UUID
    created_at: datetime.datetime
