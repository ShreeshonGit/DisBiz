import time
from typing import Dict, Any, List

class SchedulerMonitor:
    """
    Tracks and compiles telemetry statistics for the scheduler execution pool.
    """
    def __init__(self) -> None:
        self.start_time = time.time()
        self.total_runs = 0
        self.successes = 0
        self.failures = 0
        self.retries = 0
        self.durations: List[float] = []

    def record_run(self, duration: float, success: bool, retries: int = 0) -> None:
        """
        Logs a completed scraper run's duration and status.
        """
        self.total_runs += 1
        if success:
            self.successes += 1
        else:
            self.failures += 1
        self.retries += retries
        self.durations.append(duration)

    def get_metrics(self, current_queue_size: int, active_worker_count: int, max_workers: int) -> Dict[str, Any]:
        """
        Compiles and returns the metrics payload.
        """
        avg_runtime = 0.0
        longest_runtime = 0.0
        if self.durations:
            avg_runtime = sum(self.durations) / len(self.durations)
            longest_runtime = max(self.durations)
            
        success_rate = 0.0
        failure_rate = 0.0
        if self.total_runs > 0:
            success_rate = (self.successes / self.total_runs) * 100.0
            failure_rate = (self.failures / self.total_runs) * 100.0
            
        worker_utilization = 0.0
        if max_workers > 0:
            worker_utilization = (active_worker_count / max_workers) * 100.0
            
        return {
            "uptime_seconds": time.time() - self.start_time,
            "total_runs": self.total_runs,
            "successes": self.successes,
            "failures": self.failures,
            "retries": self.retries,
            "success_rate": round(success_rate, 1),
            "failure_rate": round(failure_rate, 1),
            "avg_runtime_seconds": round(avg_runtime, 2),
            "longest_runtime_seconds": round(longest_runtime, 2),
            "queue_size": current_queue_size,
            "active_workers": active_worker_count,
            "worker_utilization": round(worker_utilization, 1)
        }
