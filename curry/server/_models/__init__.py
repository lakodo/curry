"""Loads all SQLModel models for alembic migrations"""

from curry.server.resources.hero import Hero

__all__ = [
    "Hero",
]
