from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
from app.endpoints import users
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key='your-secret-key')

app = FastAPI(title="Image Processing Service", version='0.2.0',
              contact={'name': 'Oluwatooki', 'email': 'oluwatooki@gmail.com'},
              description="An Image Processing service for image manipulation tasks like "
                          "resizing, cropping, filtering, and format conversion."
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


@app.get('/',
         summary="Root Endpoint",
         description="Returns a simple 'Hello World' message.")
async def root():
    """Root endpoint returning a simple message."""
    return {"Detail": "This is An Image Processing service"}
