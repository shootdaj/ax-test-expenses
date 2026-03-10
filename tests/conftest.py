"""Shared test fixtures."""

import pytest

from app import app as flask_app
from app.models import reset_db


@pytest.fixture
def app():
    """Create application for testing."""
    flask_app.config["TESTING"] = True
    yield flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db():
    """Reset the in-memory database before each test."""
    reset_db()
    yield
    reset_db()
