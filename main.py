from fastapi import FastAPI
import sys,os
from fastapi.middleware.cors import CORSMiddleware
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.routes import api_router

# Add the project root to sys.path so that 'schemas' can be found when this file is run directly

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
    "*"
    # Add other allowed origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allows cookies, authorization headers, etc.
    allow_methods=["*"],     # Allows all standard methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allows all headers
)

app.include_router(api_router)


# from pydantic import BaseModel

# class Item(BaseModel):
#     name: str
#     description: str


@app.get("/")
async def root():
    return {"message": "Hello World"}