import time
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings


# Load environment variables from .env file


def get_db():
    """Returns conn, cursor\n
     The Connection and the cursor used to execute commands"""
    while True:
        try:
            conn = psycopg2.connect(
                database=settings.DATABASE_NAME,
                user=settings.DATABASE_USERNAME,
                password=settings.DATABASE_PASSWORD,
                port=settings.DATABASE_PORT,
                cursor_factory=RealDictCursor
            )
            cursor = conn.cursor()
            break
        except Exception as error:
            print(f"Connecting to database Failed.\nERROR: {error}")
            time.sleep(2)
    return conn, cursor
