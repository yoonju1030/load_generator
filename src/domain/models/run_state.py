# app/domain/models/run_state.py
from dataclasses import dataclass, field
from typing import Optional
import asyncio
import time

@dataclass
class Stats:
    sent: int = 0
    success: int = 0
    fail: int = 0
    latency_ms: list[float] = field(default_factory=list)

@dataclass
class RunState:
    run_id: str
    status: str  # "running" | "stopped" | "failed"
    started_at: float
    duration_s: int
    stop_event: asyncio.Event
    task: asyncio.Task
    stats: Stats
    error: Optional[str] = None
