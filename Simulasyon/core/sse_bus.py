# Simulasyon/core/sse_bus.py
import asyncio
import json
from typing import Optional, Set

# SSE'ye bağlı client'lar
_subscribers: Set[asyncio.Queue] = set()

# FastAPI'nin event loop'u
_server_loop: Optional[asyncio.AbstractEventLoop] = None


def set_server_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _server_loop
    _server_loop = loop


def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue(maxsize=1000)
    _subscribers.add(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    _subscribers.discard(q)


async def _broadcast(alarm: dict) -> None:
    """
    Alarmı tüm SSE client'larına dağıtır
    """
    if not _subscribers:
        return

    payload = json.dumps(alarm, ensure_ascii=False)

    for q in list(_subscribers):
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass
        except Exception:
            _subscribers.discard(q)


def publish_alarm_threadsafe(alarm: dict) -> None:
    """
    Alarm hangi thread'den gelirse gelsin
    FastAPI event loop'unda publish eder
    """
    if _server_loop is None:
        raise RuntimeError("SSE server loop ayarlanmadı")

    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        running_loop = None

    if running_loop is _server_loop:
        asyncio.create_task(_broadcast(alarm))
    else:
        asyncio.run_coroutine_threadsafe(
            _broadcast(alarm),
            _server_loop
        )
