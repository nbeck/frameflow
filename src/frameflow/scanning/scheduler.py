"""Background scan scheduler."""

from frameflow.scanning.scanner import PhotoScanner


class ScanScheduler:
    """Trigger background scans."""

    def __init__(self, scanner: PhotoScanner) -> None:
        self._scanner = scanner

    def run_once(self) -> int:
        """Run a single scan immediately."""

        return self._scanner.scan()
