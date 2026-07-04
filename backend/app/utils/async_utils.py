import asyncio
import logging
from typing import Coroutine, Any

logger = logging.getLogger(__name__)

# Global set to maintain strong references to active background tasks
background_tasks = set()

def safe_create_task(coro: Coroutine[Any, Any, Any], name: str = None) -> asyncio.Task:
    """
    Spawns a background task safely:
    1. Keeps a strong reference in background_tasks to prevent early garbage collection.
    2. Attaches a callback to log any unhandled exceptions to logger.exception.
    """
    task = asyncio.create_task(coro, name=name)
    background_tasks.add(task)
    
    def done_callback(t: asyncio.Task) -> None:
        background_tasks.discard(t)
        try:
            if not t.cancelled():
                exc = t.exception()
                if exc:
                    logger.error(
                        f"Unhandled exception in background task '{t.get_name()}':",
                        exc_info=exc
                    )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in background task callback: {e}")
            
    task.add_done_callback(done_callback)
    return task
