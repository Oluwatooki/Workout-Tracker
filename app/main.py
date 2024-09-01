from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints import (
    users,
    login,
    exercises,
    workout,
    scheduled_workouts,
    workout_logs,
)
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Workout Tracker",
    version="0.2.0",
    contact={"name": "Oluwatooki", "email": "oluwatooki@gmail.com"},
    description="A Workout Tracker where users can"
    " Based on https://roadmap.sh/projects/image-processing-service",
    # dependencies=[Depends(utils.validate_api_key)]
)

origins = [""]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(login.router)
app.include_router(exercises.router)
app.include_router(workout.router)
app.include_router(scheduled_workouts.router)
app.include_router(workout_logs.router)


@app.get("/", summary="Root Endpoint", description="Returns a simple message.")
async def root():
    """Root endpoint returning a simple message."""
    return {"Detail": "This is An Workout Tracker API"}
