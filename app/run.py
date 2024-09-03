import logging
import uvicorn
from app.db.seeds.seed_exercises import seed_exercise_data
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info('Application Starting')
    seed_exercise_data()
    uvicorn.run('app.main:app', host="127.0.0.1", port=8000,reload=True)
