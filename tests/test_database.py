"""Tests for database initialization and schema."""

import sqlite3

import pytest

from init_db import init_database


def test_database_creation(temp_db):
    """Test that database is created with all required tables."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    expected_tables = [
        "users",
        "income_sources",
        "paycheck_deductions",
        "pay_periods",
        "expense_categories",
        "monthly_expenses",
        "savings_goals",
        "budget_periods",
    ]

    for table in expected_tables:
        assert table in tables, f"Table {table} not found in database"

    conn.close()


def test_default_expense_categories(temp_db):
    """Test that default expense categories are created."""
    init_database(temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM expense_categories")
    count = cursor.fetchone()[0]

    assert count > 0, "No default expense categories were created"
    assert count >= 10, "Expected at least 10 default categories"

    # Check for specific categories
    cursor.execute("SELECT name FROM expense_categories WHERE name = ?", ("Groceries",))
    assert cursor.fetchone() is not None, "Groceries category not found"

    conn.close()


def test_users_table_structure(initialized_db):
    """Test users table has correct structure."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    assert "id" in columns
    assert "name" in columns
    assert "is_active" in columns
    assert "created_at" in columns

    conn.close()


def test_income_sources_table_constraints(initialized_db):
    """Test income_sources table constraints."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Create a test user first
    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Test User",))
    user_id = cursor.lastrowid

    # Test valid pay frequency
    cursor.execute(
        """
        INSERT INTO income_sources (user_id, name, annual_salary, pay_frequency, first_pay_date)
        VALUES (?, ?, ?, ?, ?)
    """,
        (user_id, "Test Job", 50000, "bi-weekly", "2024-01-01"),
    )
    conn.commit()

    # Test invalid pay frequency should fail
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO income_sources (user_id, name, annual_salary, pay_frequency, first_pay_date)
            VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, "Bad Job", 50000, "invalid", "2024-01-01"),
        )
        conn.commit()

    conn.close()


def test_paycheck_deductions_constraints(initialized_db, sample_income_source):
    """Test paycheck_deductions table constraints."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Test valid calculation types
    valid_types = ["percentage", "fixed_per_paycheck", "fixed_annual"]

    for calc_type in valid_types:
        cursor.execute(
            """
            INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount)
            VALUES (?, ?, ?, ?)
        """,
            (sample_income_source, f"Test {calc_type}", calc_type, 100),
        )
        conn.commit()

    # Test invalid calculation type should fail
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount)
            VALUES (?, ?, ?, ?)
        """,
            (sample_income_source, "Bad Deduction", "invalid_type", 100),
        )
        conn.commit()

    conn.close()


def test_monthly_expenses_unique_constraint(initialized_db):
    """Test that monthly_expenses enforces unique constraint."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Get a category
    cursor.execute("SELECT id FROM expense_categories LIMIT 1")
    category_id = cursor.fetchone()[0]

    # Insert first expense
    cursor.execute(
        """
        INSERT INTO monthly_expenses (category_id, year, month, planned_amount)
        VALUES (?, ?, ?, ?)
    """,
        (category_id, 2024, 1, 500),
    )
    conn.commit()

    # Try to insert duplicate - should fail
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO monthly_expenses (category_id, year, month, planned_amount)
            VALUES (?, ?, ?, ?)
        """,
            (category_id, 2024, 1, 600),
        )
        conn.commit()

    conn.close()


def test_pay_periods_unique_constraint(initialized_db, sample_income_source):
    """Test that pay_periods enforces unique constraint on income_source and date."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Insert first pay period
    cursor.execute(
        """
        INSERT INTO pay_periods (income_source_id, pay_date, gross_amount, year)
        VALUES (?, ?, ?, ?)
    """,
        (sample_income_source, "2024-01-05", 2000, 2024),
    )
    conn.commit()

    # Try to insert duplicate - should fail
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """
            INSERT INTO pay_periods (income_source_id, pay_date, gross_amount, year)
            VALUES (?, ?, ?, ?)
        """,
            (sample_income_source, "2024-01-05", 2000, 2024),
        )
        conn.commit()

    conn.close()
