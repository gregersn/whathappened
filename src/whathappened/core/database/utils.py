"""Database utility functions."""

from whathappened.core.database import Base


def get_class_by_tablename(tablename):
    """Get a class based on tablename."""

    for c in Base.registry._class_registry.values():
        if hasattr(c, "__tablename__") and c.__tablename__ == tablename:
            return c
