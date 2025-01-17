"""Utility functions for characters."""

from typing import Any, Union


def datetimeformat(value, formatstring: str = "%Y-%m-%d %H:%M:%S"):
    """Jinja filter for formatting datetimes."""
    return value.strftime(formatstring)


def valuetostring(value: Union[str, dict[Any, Any]]):
    """Convert a value to string"""
    if isinstance(value, dict):
        return ", ".join(f"{k}: {v}" for k, v in value.items())
    return value
