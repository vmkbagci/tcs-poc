"""Pytest configuration and fixtures for tcs-store tests."""

import pytest
from tcs_store.main import store


@pytest.fixture(autouse=True)
def clear_store():
    """Clear the in-memory store before each test."""
    store.clear()
    yield
    store.clear()
