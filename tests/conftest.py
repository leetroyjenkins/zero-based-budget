"""Pytest configuration and fixtures."""

import os
import sqlite3
import tempfile

import pytest


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    # Remove the file so init_database will create it fresh with default data
    os.remove(path)
    yield path
    # Cleanup with retry for Windows file locking
    try:
        if os.path.exists(path):
            os.remove(path)
    except PermissionError:
        import gc
        import time

        gc.collect()  # Force garbage collection to close any lingering connections
        time.sleep(0.1)
        try:
            if os.path.exists(path):
                os.remove(path)
        except PermissionError:
            pass  # If still locked, leave it for OS cleanup


@pytest.fixture
def initialized_db(temp_db):
    """Create and initialize a test database."""
    from init_db import init_database

    init_database(temp_db)
    yield temp_db


@pytest.fixture
def sample_user(initialized_db):
    """Create a sample user for testing."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, is_active) VALUES (?, ?)", ("Test User", 1))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


@pytest.fixture
def sample_income_source(initialized_db, sample_user):
    """Create a sample income source for testing."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO income_sources (user_id, name, annual_salary, pay_frequency, first_pay_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (sample_user, "Test Job", 52000.0, "bi-weekly", "2024-01-05", 1),
    )
    conn.commit()
    income_source_id = cursor.lastrowid
    conn.close()
    return income_source_id
