from fastapi import APIRouter
from src.routers.run import run_router

api_router=APIRouter()
api_router.include_router(run_router)
