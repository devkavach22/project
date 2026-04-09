from fastapi import APIRouter
from app.api.CV_data_api import router as cv_parser_router
# from app.api.pdf_parser import router as pdf_parser_router



api_router = APIRouter()

api_router.include_router(cv_parser_router,prefix="/api",tags=["CV Parser"])
# api_router.include_router(pdf_parser_router,prefix="/api",tags=["PDF Parser"])


