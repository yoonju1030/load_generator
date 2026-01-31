from fastapi import APIRouter, HTTPException
from src.services.test import TestService

test_router = APIRouter(prefix="/test")
test_service = TestService()

@test_router.get("/get_test")
def get_test():
    try:
        result = test_service.make_result()
        return result
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
