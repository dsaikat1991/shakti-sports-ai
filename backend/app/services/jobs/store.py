from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class Job:
    id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    result: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "result": self.result,
            "error": self.error,
        }


@dataclass(slots=True)
class JobStore:
    """
    In-memory job store for background video analysis.

    This is an MVP-scoped choice, not a production job queue: state is
    lost on restart and isn't shared across multiple server processes.
    Fine for a single-process deployment; revisit (Redis/DB-backed
    store, or a real task queue like Celery/RQ) before running more
    than one worker process, since requests could round-robin to a
    process that never ran the job.
    """

    _jobs: dict[str, Job] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def create(self) -> Job:
        now = datetime.now(timezone.utc)
        job = Job(
            id=str(uuid.uuid4()),
            status=JobStatus.QUEUED,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def mark_processing(self, job_id: str) -> None:
        self._update(job_id, status=JobStatus.PROCESSING)

    def mark_completed(self, job_id: str, result: dict[str, Any]) -> None:
        self._update(job_id, status=JobStatus.COMPLETED, result=result)

    def mark_failed(self, job_id: str, error: str) -> None:
        self._update(job_id, status=JobStatus.FAILED, error=error)

    def _update(
        self,
        job_id: str,
        *,
        status: JobStatus,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            job.status = status
            job.updated_at = datetime.now(timezone.utc)
            if result is not None:
                job.result = result
            if error is not None:
                job.error = error

    def prune_finished_older_than(self, *, minutes: int) -> int:
        """Drop completed/failed jobs older than the cutoff to bound memory growth.

        Never prunes queued/processing jobs, even if old, since a client
        may still be about to poll for them.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        removed = 0
        with self._lock:
            stale_ids = [
                job_id
                for job_id, job in self._jobs.items()
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED)
                and job.updated_at < cutoff
            ]
            for job_id in stale_ids:
                del self._jobs[job_id]
                removed += 1
        return removed


job_store = JobStore()
