import logging
import asyncio
from datetime import datetime
from collections import deque
import threading
from typing import Dict, Any, List

class MemoryLogRecord:
    def __init__(self, record: logging.LogRecord):
        self.timestamp = datetime.fromtimestamp(record.created).isoformat()
        self.level = record.levelname
        self.logger_name = record.name
        self.message = record.getMessage()
        self.traceback = None
        if record.exc_info:
            import traceback
            self.traceback = "".join(traceback.format_exception(*record.exc_info))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "logger": self.logger_name,
            "message": self.message,
            "traceback": self.traceback
        }

class MemoryLogHandler(logging.Handler):
    def __init__(self, max_records=2000):
        super().__init__()
        self.max_records = max_records
        self.records = deque(maxlen=max_records)
        self.lock = threading.RLock()
        self.listeners = []

    def emit(self, record):
        try:
            log_record = MemoryLogRecord(record)
            log_dict = log_record.to_dict()
            with self.lock:
                self.records.append(log_dict)
            
            # Notify any active SSE stream listeners outside the lock to prevent recursion deadlocks
            for listener in list(self.listeners):
                try:
                    import asyncio
                    loop = asyncio.get_running_loop()
                    loop.create_task(listener(log_dict))
                except RuntimeError:
                    # No running loop in this thread context (common in sync threads)
                    pass
                except Exception:
                    try:
                        self.listeners.remove(listener)
                    except ValueError:
                        pass
        except Exception:
            self.handleError(record)

    def get_logs(self, level: str = None, query: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self.lock:
            filtered = list(self.records)
            
        if level and level.strip():
            level_upper = level.upper().strip()
            filtered = [r for r in filtered if r["level"] == level_upper]
            
        if query and query.strip():
            query_lower = query.lower().strip()
            filtered = [
                r for r in filtered 
                if query_lower in r["message"].lower() or (r["traceback"] and query_lower in r["traceback"].lower())
            ]
            
        return filtered[-limit:]

    def get_error_groups(self) -> List[Dict[str, Any]]:
        """Groups error logs by exception message or traceback similarity."""
        with self.lock:
            errors = [r for r in self.records if r["level"] in ["ERROR", "CRITICAL"]]
            
        groups = {}
        for err in errors:
            key = err["message"]
            if err["traceback"]:
                lines = err["traceback"].strip().split("\n")
                if lines:
                    key = lines[-1]
            if key not in groups:
                groups[key] = {
                    "message": key,
                    "count": 0,
                    "last_occurrence": err["timestamp"],
                    "examples": []
                }
            groups[key]["count"] += 1
            groups[key]["last_occurrence"] = err["timestamp"]
            if len(groups[key]["examples"]) < 3:
                groups[key]["examples"].append(err)
                
        return list(groups.values())

# Global singleton memory log handler instance
memory_log_handler = MemoryLogHandler()

def setup_memory_logging():
    """Attaches the MemoryLogHandler to the root logger."""
    root_logger = logging.getLogger()
    # Check if already added
    for h in root_logger.handlers:
        if isinstance(h, MemoryLogHandler):
            return
    root_logger.addHandler(memory_log_handler)
