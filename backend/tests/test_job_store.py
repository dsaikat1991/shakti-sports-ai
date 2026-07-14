import time
import unittest
from datetime import datetime, timedelta, timezone

from app.services.jobs.store import JobStatus, JobStore


class TestJobStore(unittest.TestCase):
    def test_create_starts_queued(self) -> None:
        store = JobStore()
        job = store.create()

        self.assertEqual(job.status, JobStatus.QUEUED)
        self.assertIsNone(job.result)
        self.assertIsNone(job.error)
        self.assertIs(store.get(job.id), job)

    def test_mark_processing_then_completed(self) -> None:
        store = JobStore()
        job = store.create()

        store.mark_processing(job.id)
        self.assertEqual(store.get(job.id).status, JobStatus.PROCESSING)

        store.mark_completed(job.id, {"ok": True})
        updated = store.get(job.id)
        self.assertEqual(updated.status, JobStatus.COMPLETED)
        self.assertEqual(updated.result, {"ok": True})

    def test_mark_failed_records_error(self) -> None:
        store = JobStore()
        job = store.create()

        store.mark_failed(job.id, "boom")
        updated = store.get(job.id)
        self.assertEqual(updated.status, JobStatus.FAILED)
        self.assertEqual(updated.error, "boom")

    def test_update_on_unknown_job_id_does_not_raise(self) -> None:
        store = JobStore()
        store.mark_completed("does-not-exist", {"ok": True})  # should be a no-op

    def test_get_unknown_job_returns_none(self) -> None:
        store = JobStore()
        self.assertIsNone(store.get("does-not-exist"))

    def test_prune_removes_only_old_finished_jobs(self) -> None:
        store = JobStore()

        old_completed = store.create()
        store.mark_completed(old_completed.id, {})
        store.get(old_completed.id).updated_at = datetime.now(timezone.utc) - timedelta(minutes=120)

        recent_completed = store.create()
        store.mark_completed(recent_completed.id, {})

        still_processing = store.create()
        store.mark_processing(still_processing.id)
        store.get(still_processing.id).updated_at = datetime.now(timezone.utc) - timedelta(minutes=120)

        removed = store.prune_finished_older_than(minutes=60)

        self.assertEqual(removed, 1)
        self.assertIsNone(store.get(old_completed.id))
        self.assertIsNotNone(store.get(recent_completed.id))
        # Old but still in-flight jobs must never be pruned.
        self.assertIsNotNone(store.get(still_processing.id))

    def test_to_dict_shape(self) -> None:
        store = JobStore()
        job = store.create()
        payload = job.to_dict()

        self.assertEqual(payload["job_id"], job.id)
        self.assertEqual(payload["status"], "queued")
        self.assertIn("created_at", payload)
        self.assertIn("updated_at", payload)


if __name__ == "__main__":
    unittest.main()
