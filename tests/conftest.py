"""
Pytest configuration and shared fixtures.
"""
import os
import pytest


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """Set test environment variables."""
    # Set a dummy OpenAI API key for testing
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-for-testing")

