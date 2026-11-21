"""Explicit fail-closed gates for retired direct-execution interfaces."""
from __future__ import annotations


def legacy_gui_execution_enabled() -> bool:
    """Legacy Qt direct dispatch is retired; environment flags cannot enable it."""
    return False
