"""
Background job management system for long-running ingestion tasks.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, List, Any
from enum import Enum
from dataclasses import dataclass, asdict
from threading import Lock

from config import MAX_CONCURRENT_JOBS


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Job:
    id: str
    type: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    progress: Optional[Dict[str, Any]] = None  # {"current": 10, "total": 100, "percentage": 10.0, "message": "Processing..."}

    def to_dict(self):
        data = asdict(self)
        # Convert datetime to ISO format
        for key in ['created_at', 'started_at', 'completed_at']:
            if data[key]:
                data[key] = data[key].isoformat()
        return data

class JobManager:
    """Singleton job manager for tracking background tasks"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.jobs: Dict[str, Job] = {} # type: ignore
                    cls._instance.max_concurrent_jobs = MAX_CONCURRENT_JOBS
        return cls._instance

    def create_job(self, job_type: str, params: Optional[Dict[str, Any]] = None) -> Job:
        """Create a new job"""
        job = Job(
            id=str(uuid.uuid4()),
            type=job_type,
            status=JobStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            params=params
        )
        self.jobs[job.id] = job
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)

    def get_all_jobs(self) -> List[Job]:
        """Get all jobs, sorted by creation time (newest first)"""
        return sorted(self.jobs.values(), key=lambda j: j.created_at, reverse=True)

    def get_running_jobs(self) -> List[Job]:
        """Get all currently running jobs"""
        return [j for j in self.jobs.values() if j.status == JobStatus.RUNNING]

    def can_start_job(self) -> bool:
        """Check if we can start a new job (based on concurrent limit)"""
        return len(self.get_running_jobs()) < self.max_concurrent_jobs

    def start_job(self, job_id: str):
        """Mark job as running"""
        if job := self.jobs.get(job_id):
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)

    def complete_job(self, job_id: str, result: Dict[str, Any]):
        """Mark job as completed with result"""
        if job := self.jobs.get(job_id):
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            job.result = result

    def fail_job(self, job_id: str, error: str):
        """Mark job as failed with error message"""
        if job := self.jobs.get(job_id):
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now(timezone.utc)
            job.error = error

    def update_progress(self, job_id: str, current: int, total: int, message: str = ""):
        """Update job progress"""
        if job := self.jobs.get(job_id):
            percentage = (current / total * 100) if total > 0 else 0
            job.progress = {
                "current": current,
                "total": total,
                "percentage": round(percentage, 2),
                "message": message
            }

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.
        Note: This only marks the job as cancelled. The actual background task
        needs to check job status periodically to respect cancellation.
        """
        if job := self.jobs.get(job_id):
            if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.now(timezone.utc)
                return True
        return False

    def is_job_cancelled(self, job_id: str) -> bool:
        """Check if a job has been cancelled"""
        if job := self.jobs.get(job_id):
            return job.status == JobStatus.CANCELLED
        return False

    def cleanup_old_jobs(self, max_jobs: int = 100):
        """Keep only the most recent jobs"""
        if len(self.jobs) > max_jobs:
            all_jobs = sorted(self.jobs.values(), key=lambda j: j.created_at, reverse=True)
            jobs_to_keep = {j.id for j in all_jobs[:max_jobs]}
            self.jobs = {jid: j for jid, j in self.jobs.items() if jid in jobs_to_keep}

# Global job manager instance
job_manager = JobManager()
