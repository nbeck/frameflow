from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from frameflow.scanning import ScanScheduler, SyncState

pytestmark = pytest.mark.unit


def test_scheduler_runs_scan() -> None:
    scanner = Mock()
    scanner.scan.return_value = 42

    scheduler = ScanScheduler(scanner)

    assert scheduler.run_once() == 42


def test_run_once_updates_sync_state() -> None:
    scanner = Mock()
    scanner.scan.return_value = 7
    state = SyncState()

    scheduler = ScanScheduler(scanner, sync_state=state)
    scheduler.run_once()

    assert state.last_sync_photos_processed == 7
    assert state.last_sync_completed_at is not None
    assert state.sync_running is False


def test_run_once_records_completion_timestamp() -> None:
    before = datetime.now(UTC)
    scanner = Mock()
    scanner.scan.return_value = 0
    state = SyncState()

    ScanScheduler(scanner, sync_state=state).run_once()

    assert state.last_sync_completed_at is not None
    assert state.last_sync_completed_at >= before


def test_sync_running_false_after_completion() -> None:
    scanner = Mock()
    scanner.scan.return_value = 0
    state = SyncState()

    ScanScheduler(scanner, sync_state=state).run_once()

    assert state.sync_running is False


def test_sync_state_starts_empty() -> None:
    state = SyncState()

    assert state.last_sync_completed_at is None
    assert state.last_sync_photos_processed is None
    assert state.sync_running is False


def test_scheduler_uses_private_state_when_none_provided() -> None:
    scanner = Mock()
    scanner.scan.return_value = 3

    scheduler = ScanScheduler(scanner)
    result = scheduler.run_once()

    assert result == 3


def test_run_once_does_not_record_completion_on_failure() -> None:
    scanner = Mock()
    scanner.scan.side_effect = RuntimeError("scan failed")
    state = SyncState()

    with pytest.raises(RuntimeError, match="scan failed"):
        ScanScheduler(scanner, sync_state=state).run_once()

    assert state.sync_running is False
    assert state.last_sync_completed_at is None
    assert state.last_sync_photos_processed is None
