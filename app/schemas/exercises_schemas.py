from pydantic import BaseModel


class ExerciseModel(BaseModel):
    exercise_id: int | str
    name: str
    description: str
    category: str

