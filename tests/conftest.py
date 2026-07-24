"""Shared pytest fixtures for the Suncoin test suite."""

from __future__ import annotations

import pytest

from suncoin import Blockchain


@pytest.fixture
def chain() -> Blockchain:
    """A fresh chain at a low difficulty so mining is fast in tests."""
    return Blockchain(difficulty=2, mining_reward=50.0)
