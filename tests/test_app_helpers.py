"""Tests for app helper functions (non-UI components)."""

import sqlite3
from datetime import datetime


def test_database_connection_helper(initialized_db, monkeypatch):
    """Test that database connection helper works correctly."""
    # We can't directly test the app's get_db_connection without importing app
    # which would trigger Streamlit, so we test the pattern instead
    conn = sqlite3.connect(initialized_db)
    assert conn is not None

    # Verify we can query
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    assert len(tables) > 0

    conn.close()


def test_expense_category_retrieval(initialized_db):
    """Test retrieving expense categories."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, is_fixed FROM expense_categories")
    categories = cursor.fetchall()

    assert len(categories) > 0, "No categories found"

    # Verify structure
    for cat_id, name, is_fixed in categories:
        assert isinstance(cat_id, int)
        assert isinstance(name, str)
        assert is_fixed in (0, 1)

    conn.close()


def test_user_retrieval(initialized_db, sample_user):
    """Test retrieving users from database."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, is_active FROM users WHERE id = ?", (sample_user,))
    result = cursor.fetchone()

    assert result is not None
    user_id, name, is_active = result
    assert user_id == sample_user
    assert name == "Test User"
    assert is_active == 1

    conn.close()


def test_monthly_income_calculation(initialized_db, sample_income_source):
    """Test calculating monthly income from pay periods."""
    from init_db import calculate_net_pay, generate_pay_periods

    # Generate pay periods for a specific month
    generate_pay_periods(
        initialized_db, sample_income_source, datetime(2024, 1, 1), datetime(2024, 1, 31)
    )

    calculate_net_pay(initialized_db)

    # Calculate total for January 2024
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT SUM(net_amount) as total
        FROM pay_periods
        WHERE year = ? AND strftime('%m', pay_date) = ?
    """,
        (2024, "01"),
    )

    result = cursor.fetchone()
    total_income = result[0] if result[0] else 0

    assert total_income > 0, "No income calculated for January"

    # Bi-weekly with $52k annual should have 2 pay periods in most months
    # Each pay period is roughly $2000 gross
    assert total_income > 1000, f"Expected monthly income > $1000, got ${total_income:.2f}"

    conn.close()


def test_monthly_expense_total(initialized_db):
    """Test calculating total monthly expenses."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Get a category
    cursor.execute("SELECT id FROM expense_categories LIMIT 1")
    category_id = cursor.fetchone()[0]

    # Add some expenses for January 2024
    cursor.execute(
        """
        INSERT INTO monthly_expenses (category_id, year, month, planned_amount)
        VALUES (?, ?, ?, ?)
    """,
        (category_id, 2024, 1, 500),
    )
    conn.commit()

    # Calculate total
    cursor.execute(
        """
        SELECT SUM(planned_amount) as total
        FROM monthly_expenses
        WHERE year = ? AND month = ?
    """,
        (2024, 1),
    )

    result = cursor.fetchone()
    total_expenses = result[0] if result[0] else 0

    assert total_expenses == 500, f"Expected $500, got ${total_expenses}"

    conn.close()


def test_savings_calculation(initialized_db):
    """Test calculating available savings (income - expenses)."""
    # This tests the pattern used in the dashboard

    monthly_income = 4000
    monthly_expenses = 3500
    expected_savings = 500

    savings = monthly_income - monthly_expenses

    assert savings == expected_savings
    assert savings > 0, "Savings should be positive"


def test_savings_goal_progress(initialized_db):
    """Test savings goal progress calculation."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Create a savings goal
    cursor.execute(
        """
        INSERT INTO savings_goals (name, target_amount, current_amount, target_date, is_active)
        VALUES (?, ?, ?, ?, ?)
    """,
        ("Emergency Fund", 10000, 2500, "2024-12-31", 1),
    )
    conn.commit()

    goal_id = cursor.lastrowid

    # Retrieve and calculate progress
    cursor.execute(
        """
        SELECT target_amount, current_amount
        FROM savings_goals
        WHERE id = ?
    """,
        (goal_id,),
    )

    target, current = cursor.fetchone()
    progress_percent = (current / target) * 100

    assert progress_percent == 25.0, f"Expected 25% progress, got {progress_percent}%"

    remaining = target - current
    assert remaining == 7500, f"Expected $7500 remaining, got ${remaining}"

    conn.close()


def test_expense_by_category_aggregation(initialized_db):
    """Test aggregating expenses by category."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Get multiple categories
    cursor.execute("SELECT id FROM expense_categories LIMIT 3")
    categories = [row[0] for row in cursor.fetchall()]

    # Add expenses for each category
    for i, cat_id in enumerate(categories):
        cursor.execute(
            """
            INSERT INTO monthly_expenses (category_id, year, month, planned_amount)
            VALUES (?, ?, ?, ?)
        """,
            (cat_id, 2024, 1, (i + 1) * 100),
        )
    conn.commit()

    # Aggregate by category
    cursor.execute(
        """
        SELECT c.name, SUM(e.planned_amount) as total
        FROM monthly_expenses e
        JOIN expense_categories c ON e.category_id = c.id
        WHERE e.year = ? AND e.month = ?
        GROUP BY c.id, c.name
        ORDER BY total DESC
    """,
        (2024, 1),
    )

    results = cursor.fetchall()

    assert len(results) == 3, f"Expected 3 categories, got {len(results)}"

    # Verify totals
    totals = [row[1] for row in results]
    expected_totals = [300, 200, 100]
    assert totals == expected_totals, f"Expected {expected_totals}, got {totals}"

    conn.close()


def test_inactive_users_excluded(initialized_db):
    """Test that inactive users can be filtered out."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Create active and inactive users
    cursor.execute("INSERT INTO users (name, is_active) VALUES (?, ?)", ("Active User", 1))
    cursor.execute("INSERT INTO users (name, is_active) VALUES (?, ?)", ("Inactive User", 0))
    conn.commit()

    # Query only active users
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    active_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_count = cursor.fetchone()[0]

    assert total_count > active_count, "Should have at least one inactive user"
    assert active_count >= 1, "Should have at least one active user"

    conn.close()


def test_inactive_deductions_excluded(initialized_db, sample_income_source):
    """Test that inactive deductions are excluded from calculations."""
    from init_db import calculate_net_pay, generate_pay_periods

    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Generate a pay period
    generate_pay_periods(
        initialized_db, sample_income_source, datetime(2024, 1, 5), datetime(2024, 1, 5)
    )

    # Add active deduction
    cursor.execute(
        """
        INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount, is_pre_tax, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (sample_income_source, "Active Tax", "percentage", 10, 0, 1),
    )

    # Add inactive deduction
    cursor.execute(
        """
        INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount, is_pre_tax, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (sample_income_source, "Inactive Tax", "percentage", 20, 0, 0),
    )

    conn.commit()

    # Calculate net pay
    calculate_net_pay(initialized_db)

    # Verify only active deduction was applied
    cursor.execute(
        "SELECT gross_amount, net_amount FROM pay_periods WHERE income_source_id = ?",
        (sample_income_source,),
    )
    gross, net = cursor.fetchone()

    # Only 10% should be deducted, not 30%
    expected_net = gross * 0.90
    assert abs(net - expected_net) < 0.01, f"Expected ${expected_net:.2f}, got ${net:.2f}"

    conn.close()
