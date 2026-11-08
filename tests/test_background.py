"""Blender-free tests for `core.background`.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import asyncio
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.background import BackgroundTask  # noqa: E402

TIMEOUT = 5


class BackgroundTaskTests(unittest.TestCase):
    def test_returns_the_coroutine_value(self):
        async def work():
            await asyncio.sleep(0)
            return 42

        task = BackgroundTask().start(work)
        self.assertTrue(task.wait(TIMEOUT))
        self.assertTrue(task.done())
        self.assertEqual(task.result(), 42)

    def test_runs_on_a_worker_thread(self):
        async def work():
            return threading.current_thread()

        task = BackgroundTask().start(work)
        task.wait(TIMEOUT)
        self.assertIsNot(task.result(), threading.current_thread())

    def test_reraises_the_worker_exception(self):
        async def work():
            raise ValueError("boom")

        task = BackgroundTask().start(work)
        task.wait(TIMEOUT)
        with self.assertRaisesRegex(ValueError, "boom"):
            task.result()

    def test_result_before_done_raises(self):
        release = threading.Event()

        async def work():
            await asyncio.to_thread(release.wait, TIMEOUT)

        task = BackgroundTask().start(work)
        try:
            self.assertFalse(task.done())
            with self.assertRaises(RuntimeError):
                task.result()
        finally:
            release.set()
            task.wait(TIMEOUT)

    def test_events_arrive_in_order(self):
        task = BackgroundTask()

        async def work():
            for i in range(5):
                task.publish(i)

        task.start(work).wait(TIMEOUT)
        self.assertEqual(task.drain(), [0, 1, 2, 3, 4])
        self.assertEqual(task.drain(), [])

    def test_cancel_is_visible_to_the_work(self):
        task = BackgroundTask()
        started = threading.Event()

        async def work():
            started.set()
            while not task.cancelled():
                await asyncio.sleep(0.01)
            return "stopped"

        task.start(work)
        self.assertTrue(started.wait(TIMEOUT))
        task.cancel()
        self.assertTrue(task.wait(TIMEOUT))
        self.assertEqual(task.result(), "stopped")

    def test_tasks_are_independent(self):
        async def value(n):
            await asyncio.sleep(0.01)
            return n

        tasks = [BackgroundTask().start(lambda n=n: value(n)) for n in range(4)]
        tasks[0].cancel()
        for task in tasks:
            task.wait(TIMEOUT)
        self.assertEqual([t.result() for t in tasks], [0, 1, 2, 3])
        self.assertEqual([t.cancelled() for t in tasks], [True, False, False, False])

    def test_start_twice_raises(self):
        async def work():
            return None

        task = BackgroundTask().start(work)
        with self.assertRaises(RuntimeError):
            task.start(work)
        task.wait(TIMEOUT)


if __name__ == "__main__":
    unittest.main()
