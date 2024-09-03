from pydantic import BaseModel,Field


class ExerciseModel(BaseModel):
    exercise_id: int = Field(..., example=1)
    name: str = Field(..., example="Push Up")
    description: str = Field(..., example="A basic push-up exercise.")
    category: str = Field(..., example="strength")
