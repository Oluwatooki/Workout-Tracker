import logging
import uvicorn
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info('Application Starting')
    uvicorn.run('app.main:app', host="127.0.0.1", port=8000,reload=True)
