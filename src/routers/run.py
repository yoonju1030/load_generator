from fastapi import APIRouter, HTTPException
from app.domain.schemas.run import RunCreateRequest
from src.services.run_manager import RunManager

run_router = APIRouter(prefix="/run")
manager = RunManager()

@run_router.post("")
async def create_run(req: RunCreateRequest):
    try:
        run_id = manager.start(req)
        return {"run_id": run_id}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@run_router.post("/{run_id}/stop")
async def stop_run(run_id: str):
    try:
        ok = manager.stop(run_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Run not found")
        return {"message": "Run stopped"}
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@run_router.get("/{run_id}")
async def get_run(run_id: str):
    try:
        run = manager.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return run
    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)