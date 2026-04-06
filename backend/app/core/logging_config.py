"""Centralized logging setup for backend services."""
from __future__ import annotations

import logging


def configure_logging() -> None:
    """Initialize root logger once for consistent formatting and levels."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
