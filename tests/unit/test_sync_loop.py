"""Unit tests for SyncLoop background scheduler."""

import threading
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest

from frameflow.scanning import SyncAlreadyRunningError
from frameflow.workers import SyncLoop

pytestmark = pytest.mark.unit


def _make_scheduler(run_once_side_effect: Callable[..., Any] | None = None) -> MagicMock:
    scheduler = MagicMock()
    if run_once_side_effect is not None:
        scheduler.run_once.side_effect = run_once_side_effect
    else:
        scheduler.run_once.return_value = 0
    return scheduler


def test_sync_loop_calls_run_once_after_interval() -> None:
    ran = threading.Event()

    def run_once() -> int:
        ran.set()
        return 1

    scheduler = _make_scheduler(run_once_side_effect=run_once)
    loop = SyncLoop(scheduler=scheduler, interval_seconds=0.01)
    loop.start()
    ran.wait(timeout=2.0)
    loop.stop()

    assert ran.is_set()
    scheduler.run_once.assert_called()


def test_sync_loop_does_not_run_immediately_before_interval() -> None:
    scheduler = _make_scheduler()
    loop = SyncLoop(scheduler=scheduler, interval_seconds=60.0)
    loop.start()
    loop.stop()

    scheduler.run_once.assert_not_called()


def test_sync_loop_runs_multiple_times() -> None:
    call_count = 0
    ready = threading.Event()

    def run_once() -> int:
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            ready.set()
        return call_count

    scheduler = _make_scheduler(run_once_side_effect=run_once)
    loop = SyncLoop(scheduler=scheduler, interval_seconds=0.01)
    loop.start()
    ready.wait(timeout=2.0)
    loop.stop()

    assert call_count >= 2


def test_sync_loop_stop_exits_cleanly() -> None:
    scheduler = _make_scheduler()
    loop = SyncLoop(scheduler=scheduler, interval_seconds=60.0)
    loop.start()
    loop.stop()

    assert loop._thread is None


def test_sync_loop_skips_when_already_running() -> None:
    ran = threading.Event()
    call_count = 0

    def side_effect() -> int:
        nonlocal call_count
        call_count += 1
        ran.set()
        raise SyncAlreadyRunningError()

    scheduler = _make_scheduler(run_once_side_effect=side_effect)
    loop = SyncLoop(scheduler=scheduler, interval_seconds=0.01)
    loop.start()
    ran.wait(timeout=2.0)
    loop.stop()

    assert ran.is_set()


def test_sync_loop_continues_after_exception() -> None:
    succeeded = threading.Event()
    call_count = 0

    def run_once() -> int:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("transient failure")
        succeeded.set()
        return 1

    scheduler = _make_scheduler(run_once_side_effect=run_once)
    loop = SyncLoop(scheduler=scheduler, interval_seconds=0.01)
    loop.start()
    succeeded.wait(timeout=2.0)
    loop.stop()

    assert succeeded.is_set()
    assert call_count >= 2


def test_sync_loop_stop_before_start_is_safe() -> None:
    scheduler = _make_scheduler()
    loop = SyncLoop(scheduler=scheduler, interval_seconds=60.0)
    loop.stop()


def test_sync_loop_double_start_is_safe() -> None:
    scheduler = _make_scheduler()
    loop = SyncLoop(scheduler=scheduler, interval_seconds=60.0)
    loop.start()
    thread = loop._thread
    loop.start()

    assert loop._thread is thread
    loop.stop()


def test_sync_loop_can_restart_after_stop() -> None:
    ran = threading.Event()

    def run_once() -> int:
        ran.set()
        return 0

    scheduler = _make_scheduler(run_once_side_effect=run_once)
    loop = SyncLoop(scheduler=scheduler, interval_seconds=0.01)
    loop.start()
    ran.wait(timeout=2.0)
    loop.stop()

    ran.clear()
    loop.start()
    ran.wait(timeout=2.0)
    loop.stop()

    assert ran.is_set()
