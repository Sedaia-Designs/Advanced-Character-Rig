"""Run a coroutine on a worker thread and hand its progress and result back to the main thread.

Blender's main thread must stay free to draw the UI, and `bpy` is not
thread-safe. A `BackgroundTask` runs `bpy`-free async work on its own thread
with its own event loop. The main thread (a modal operator, in Blender) polls
`done()`, reads progress with `drain()`, and collects the outcome with
`result()`, which re-raises the worker's exception on the caller's thread.

A thread blocked on a socket cannot be stopped from outside, so `cancel()`
only sets a flag. The work checks `cancelled()` at its own checkpoints, and a
request timeout bounds how long that takes.

Patterns:

- Facade: `BackgroundTask` hides `threading`, `asyncio`, and `queue` behind
  start, poll, drain, cancel, and result.
- Observer: the worker publishes events with `publish`, and the main thread
  receives them with `drain`, so the producer never calls its consumer.
"""

import asyncio
import queue
import threading
from collections.abc import Callable, Coroutine
from typing import Any


class BackgroundTask[T]:
    """One coroutine run to completion on a daemon worker thread.

    Create the task, wire anything that should `publish` to it, then `start` it::

        task = BackgroundTask()
        manager.subscribe(lambda stage, name: task.publish((stage, name)))
        task.start(lambda: manager.sync(name, should_cancel=task.cancelled))
    """

    def __init__(self):
        self._events: queue.SimpleQueue[Any] = queue.SimpleQueue()
        self._cancel = threading.Event()
        self._done = threading.Event()
        self._thread: threading.Thread | None = None
        self._result: T | None = None
        self._error: BaseException | None = None

    def start(self, make_coro: Callable[[], Coroutine[Any, Any, T]]) -> "BackgroundTask[T]":
        """Run the coroutine `make_coro()` creates on a new thread. Returns the task.

        The coroutine is created on the worker thread, inside its event loop.
        Raises `RuntimeError` if the task was already started.
        """
        if self._thread is not None:
            raise RuntimeError("BackgroundTask was already started")
        self._thread = threading.Thread(target=self._run, args=(make_coro,), daemon=True)
        self._thread.start()
        return self

    def _run(self, make_coro: Callable[[], Coroutine[Any, Any, T]]) -> None:
        try:
            self._result = asyncio.run(make_coro())
        except BaseException as error:  # Re-raised on the main thread by `result()`.
            self._error = error
        finally:
            self._done.set()

    def publish(self, event: Any) -> None:
        """Queue `event` for the main thread. Safe to call from any thread."""
        self._events.put(event)

    def drain(self) -> list[Any]:
        """Return every event published since the last call, oldest first."""
        events = []
        while True:
            try:
                events.append(self._events.get_nowait())
            except queue.Empty:
                return events

    def cancel(self) -> None:
        """Ask the work to stop at its next checkpoint."""
        self._cancel.set()

    def cancelled(self) -> bool:
        """Return whether `cancel()` was called. Pass this to the work as its cancel check."""
        return self._cancel.is_set()

    def done(self) -> bool:
        """Return whether the coroutine has finished, by returning or raising."""
        return self._done.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        """Block until the task is done or `timeout` seconds pass. Return whether it is done.

        For scripts and tests. A modal operator polls `done()` instead.
        """
        return self._done.wait(timeout)

    def result(self) -> T:
        """Return the coroutine's value, or raise its exception here.

        Raises `RuntimeError` if the task has not finished.
        """
        if not self._done.is_set():
            raise RuntimeError("BackgroundTask has not finished")
        if self._error is not None:
            raise self._error
        return self._result  # pyright: ignore[reportReturnType]
