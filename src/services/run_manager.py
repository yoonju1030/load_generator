# app/services/run_manager.py
import asyncio
import time
import uuid
from typing import Dict

import httpx
from src.db.database import async_session_factory
from src.db.models import Exec
from src.domain.models.run_state import RunState, Stats
from src.services.engine import run_load


async def _exec_insert(
    run_id: str,
    scenario,
    status_code: int | None,
    latency_ms: float | None,
    success: bool,
    error: str | None,
) -> None:
    async with async_session_factory() as session:
        row = Exec(
            run_id=run_id,
            method=scenario.method,
            path=scenario.path,
            timeout_s=scenario.timeout_s,
            request_headers=getattr(scenario, "headers", None) or None,
            request_json=getattr(scenario, "json", None),
            status_code=status_code,
            latency_ms=latency_ms,
            success=success,
            error=error,
        )
        session.add(row)
        await session.commit()


async def _notify_back(
    callback_url: str,
    run_id: str,
    status: str,
    stats: Stats,
    error: str | None = None,
) -> None:
    """Run 종료 시 callback_url로 POST 요청을 보냄."""
    body = {
        "run_id": run_id,
        "status": status,
        "sent": stats.sent,
        "success": stats.success,
        "fail": stats.fail,
    }
    if error is not None:
        body["error"] = error
    if stats.latency_ms:
        sorted_ms = sorted(stats.latency_ms)
        idx = max(0, int(len(sorted_ms) * 0.95) - 1)
        body["p95_latency_ms"] = round(sorted_ms[idx], 2)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(callback_url, json=body)
    except Exception:
        pass  # 콜백 실패는 로그만 하고 무시


class RunManager:
    def __init__(self):
        self.runs: Dict[str, RunState] = {}

    def start(self, req) -> str:
        run_id = req.run_id
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
                    run_id=run_id,
                    exec_insert=_exec_insert,
                )
                self.runs[run_id].status = "stopped"
                if getattr(req, "callback_url", None):
                    await _notify_back(
                        req.callback_url, run_id, "stopped", stats, error=None
                    )
            except Exception as e:
                self.runs[run_id].status = "failed"
                self.runs[run_id].error = str(e)
                stop.set()
                if getattr(req, "callback_url", None):
                    await _notify_back(
                        req.callback_url, run_id, "failed", stats, error=str(e)
                    )

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
