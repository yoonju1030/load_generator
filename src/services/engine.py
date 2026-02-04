# app/services/engine.py
import asyncio
import time
import httpx
from typing import Awaitable, Callable

async def fire_one(
    client: httpx.AsyncClient,
    scenario,
    sem: asyncio.Semaphore,
    stop: asyncio.Event,
    stats,
    run_id: str | None = None,
    exec_insert: Callable[..., Awaitable[None]] | None = None,
):
    start = time.perf_counter()
    status_code = None
    latency_ms = None
    success = False
    error = None
    try:
        stats.sent += 1
        resp = await client.request(
            scenario.method,
            scenario.path,
            headers=scenario.headers,
            json=scenario.json,
            timeout=scenario.timeout_s,
        )
        elapsed = (time.perf_counter() - start) * 1000
        stats.latency_ms.append(elapsed)
        status_code = resp.status_code
        latency_ms = elapsed
        success = 200 <= resp.status_code < 400
        if success:
            stats.success += 1
        else:
            stats.fail += 1
    except Exception as e:
        stats.fail += 1
        error = str(e)
        latency_ms = (time.perf_counter() - start) * 1000
    finally:
        if exec_insert and run_id:
            await exec_insert(
                run_id=run_id,
                scenario=scenario,
                status_code=status_code,
                latency_ms=latency_ms,
                success=success,
                error=error,
            )
        sem.release()

async def run_load(
    duration_s: int,
    rps: float,
    concurrency: int,
    base_url: str,
    scenario,
    stop: asyncio.Event,
    stats,
    run_id: str | None = None,
    exec_insert: Callable[..., Awaitable[None]] | None = None,
):
    sem = asyncio.Semaphore(concurrency)

    limits = httpx.Limits(
        max_connections=concurrency * 5,
        max_keepalive_connections=concurrency,
        keepalive_expiry=10.0,
    )
    timeout = httpx.Timeout(10.0)
    async with httpx.AsyncClient(base_url=base_url, limits=limits, timeout=timeout) as client:
        interval = 1.0 / rps
        end_at = time.perf_counter() + duration_s
        next_tick = time.perf_counter()

        while not stop.is_set():
            now = time.perf_counter()
            if now >= end_at:
                stop.set()
                break

            # tick 정렬 (드리프트 방지)
            if now < next_tick:
                await asyncio.sleep(next_tick - now)
            next_tick += interval

            # 동시성 제한
            await sem.acquire()

            # stop set 된 이후에는 발사하지 않게 방어
            if stop.is_set():
                sem.release()
                break

            asyncio.create_task(
                fire_one(client, scenario, sem, stop, stats, run_id=run_id, exec_insert=exec_insert)
            )

'''
- 스케줄러는 “매 1/rps 초마다 발사”를 목표로 tick을 유지
- 발사할 때마다 Semaphore로 동시성 제한
- 요청 하나는 별도 task로 실행하고 끝나면 Semaphore.release()
- 60초가 지나면 stop_event.set()해서 종료

이 방식이 “RPS 유지”와 “동시성 제한”을 가장 단순하게 같이 만족시킴.
'''