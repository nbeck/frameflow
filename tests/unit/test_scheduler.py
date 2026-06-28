from unittest.mock import Mock

from frameflow.scanning import ScanScheduler


def test_scheduler_runs_scan() -> None:
    scanner = Mock()
    scanner.scan.return_value = 42

    scheduler = ScanScheduler(scanner)

    assert scheduler.run_once() == 42
