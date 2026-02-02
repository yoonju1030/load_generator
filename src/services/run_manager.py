# app/services/run_manager.py
import asyncio, time, uuid
from typing import Dict
from app.domain.models.run_state import RunState, Stats
from app.services.engine import run_load

class RunManager:
    def __init__(self):
        self.runs: Dict[str, RunState] = {}

    def start(self, req) -> str:
        run_id = str(uuid.uuid4())
        stop = asyncio.Event()
        stats = Stats()

        async def runner():
            try:
                await run_load(
                    duration_s=req.duration_s,
                    rps=req.rps,
                    concurrency=req.concurrency,
                    base_url=req.base_url,
                    scenario=req.scenario,
                    stop=stop,
                    stats=stats,
                )
                self.runs[run_id].status = "stopped"
            except Exception as e:
                self.runs[run_id].status = "failed"
                self.runs[run_id].error = str(e)
                stop.set()

        task = asyncio.create_task(runner())
        self.runs[run_id] = RunState(
            run_id=run_id,
            status="running",
            started_at=time.time(),
            duration_s=req.duration_s,
            stop_event=stop,
            task=task,
            stats=stats,
        )
        return run_id

    def stop(self, run_id: str) -> bool:
        r = self.runs.get(run_id)
        if not r:
            return False
        r.stop_event.set()
        return True

    def get(self, run_id: str):
        return self.runs.get(run_id)
