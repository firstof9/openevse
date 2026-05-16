"""Logger adapter for OpenEVSE."""

from __future__ import annotations

import logging


class OpenEVSELoggerAdapter(logging.LoggerAdapter):
    """Prepend device name to all log messages."""

    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        """Prepend the device name."""
        return f"[{self.extra['device_name']}] {msg}", kwargs
