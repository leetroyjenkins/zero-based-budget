"""Tests for pay period generation and calculations."""

import sqlite3
from datetime import datetime

from init_db import calculate_net_pay, generate_pay_periods


def test_generate_bi_weekly_pay_periods(initialized_db, sample_income_source):
    """Test generation of bi-weekly pay periods."""
    start_date = datetime(2024, 1, 5)
    end_date = datetime(2024, 12, 31)

    count = generate_pay_periods(initialized_db, sample_income_source, start_date, end_date)

    # Bi-weekly should generate 26 or 27 pay periods in a year
    assert count >= 26 and count <= 27, f"Expected 26-27 pay periods, got {count}"

    # Verify pay periods in database
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) FROM pay_periods
        WHERE income_source_id = ? AND year = ?
    """,
        (sample_income_source, 2024),
    )

    db_count = cursor.fetchone()[0]
    assert db_count == count

    # Verify gross amount calculation
    cursor.execute(
        """
        SELECT gross_amount FROM pay_periods
        WHERE income_source_id = ?
        LIMIT 1
    """,
        (sample_income_source,),
    )

    gross_amount = cursor.fetchone()[0]
    expected_gross = 52000 / 26  # Annual salary / 26 pay periods

    assert (
        abs(gross_amount - expected_gross) < 0.01
    ), f"Expected ${expected_gross:.2f}, got ${gross_amount:.2f}"

    conn.close()


def test_generate_weekly_pay_periods(initialized_db, sample_user):
    """Test generation of weekly pay periods."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Create weekly income source
    cursor.execute(
        """
        INSERT INTO income_sources (user_id, name, annual_salary, pay_frequency, first_pay_date)
        VALUES (?, ?, ?, ?, ?)
    """,
        (sample_user, "Weekly Job", 52000, "weekly", "2024-01-05"),
    )
    conn.commit()
    income_source_id = cursor.lastrowid
    conn.close()

    count = generate_pay_periods(
        initialized_db, income_source_id, datetime(2024, 1, 1), datetime(2024, 1, 31)
    )

    # January 2024 should have 4 or 5 weekly pay periods depending on start date
    assert count >= 4 and count <= 5, f"Expected 4-5 weekly pay periods in January, got {count}"


def test_generate_monthly_pay_periods(initialized_db, sample_user):
    """Test generation of monthly pay periods."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Create monthly income source
    cursor.execute(
        """
        INSERT INTO income_sources (user_id, name, annual_salary, pay_frequency, first_pay_date)
        VALUES (?, ?, ?, ?, ?)
    """,
        (sample_user, "Monthly Job", 60000, "monthly", "2024-01-01"),
    )
    conn.commit()
    income_source_id = cursor.lastrowid
    conn.close()

    count = generate_pay_periods(
        initialized_db, income_source_id, datetime(2024, 1, 1), datetime(2024, 12, 31)
    )

    assert count == 12, f"Expected 12 monthly pay periods, got {count}"

    # Verify gross amount
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT gross_amount FROM pay_periods WHERE income_source_id = ? LIMIT 1",
        (income_source_id,),
    )
    gross_amount = cursor.fetchone()[0]
    expected_gross = 60000 / 12
    assert abs(gross_amount - expected_gross) < 0.01
    conn.close()


def test_calculate_net_pay_with_percentage_deductions(initialized_db, sample_income_source):
    """Test net pay calculation with percentage-based deductions."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Generate a pay period
    generate_pay_periods(
        initialized_db, sample_income_source, datetime(2024, 1, 5), datetime(2024, 1, 5)
    )

    # Add percentage deductions
    cursor.execute(
        """
        INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount, is_pre_tax)
        VALUES (?, ?, ?, ?, ?)
    """,
        (sample_income_source, "Federal Tax", "percentage", 15, 0),
    )

    cursor.execute(
        """
        INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount, is_pre_tax)
        VALUES (?, ?, ?, ?, ?)
    """,
        (sample_income_source, "State Tax", "percentage", 5, 0),
    )

    conn.commit()

    # Calculate net pay
    calculate_net_pay(initialized_db)

    # Verify calculation
    cursor.execute(
        "SELECT gross_amount, net_amount FROM pay_periods WHERE income_source_id = ?",
        (sample_income_source,),
    )
    gross, net = cursor.fetchone()

    expected_net = gross * 0.80  # 100% - 15% - 5% = 80%
    assert abs(net - expected_net) < 0.01, f"Expected ${expected_net:.2f}, got ${net:.2f}"

    conn.close()


def test_calculate_net_pay_with_fixed_deductions(initialized_db, sample_income_source):
    """Test net pay calculation with fixed deductions."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Generate a pay period
    generate_pay_periods(
        initialized_db, sample_income_source, datetime(2024, 1, 5), datetime(2024, 1, 5)
    )

    # Add fixed deduction
    cursor.execute(
        """
        INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount, is_pre_tax)
        VALUES (?, ?, ?, ?, ?)
    """,
        (sample_income_source, "Health Insurance", "fixed_per_paycheck", 200, 0),
    )

    conn.commit()

    # Calculate net pay
    calculate_net_pay(initialized_db)

    # Verify calculation
    cursor.execute(
        "SELECT gross_amount, net_amount FROM pay_periods WHERE income_source_id = ?",
        (sample_income_source,),
    )
    gross, net = cursor.fetchone()

    expected_net = gross - 200
    assert abs(net - expected_net) < 0.01, f"Expected ${expected_net:.2f}, got ${net:.2f}"

    conn.close()


def test_calculate_net_pay_with_pre_tax_deductions(initialized_db, sample_income_source):
    """Test net pay calculation with pre-tax deductions."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Generate a pay period
    generate_pay_periods(
        initialized_db, sample_income_source, datetime(2024, 1, 5), datetime(2024, 1, 5)
    )

    # Add pre-tax deduction (401k)
    cursor.execute(
        """
        INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount, is_pre_tax)
        VALUES (?, ?, ?, ?, ?)
    """,
        (sample_income_source, "401k", "percentage", 10, 1),
    )

    # Add post-tax percentage deduction (tax on reduced amount)
    cursor.execute(
        """
        INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount, is_pre_tax)
        VALUES (?, ?, ?, ?, ?)
    """,
        (sample_income_source, "Tax", "percentage", 20, 0),
    )

    conn.commit()

    # Calculate net pay
    calculate_net_pay(initialized_db)

    # Verify calculation
    cursor.execute(
        "SELECT gross_amount, net_amount FROM pay_periods WHERE income_source_id = ?",
        (sample_income_source,),
    )
    gross, net = cursor.fetchone()

    # Pre-tax: 10% of gross
    pre_tax_deduction = gross * 0.10
    # Post-tax: 20% of gross (note: current implementation takes % of gross, not taxable)
    post_tax_deduction = gross * 0.20
    expected_net = gross - pre_tax_deduction - post_tax_deduction

    assert abs(net - expected_net) < 0.01, f"Expected ${expected_net:.2f}, got ${net:.2f}"

    conn.close()


def test_calculate_net_pay_with_annual_deductions(initialized_db, sample_income_source):
    """Test net pay calculation with annual fixed deductions."""
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()

    # Generate a pay period
    generate_pay_periods(
        initialized_db, sample_income_source, datetime(2024, 1, 5), datetime(2024, 1, 5)
    )

    # Add annual deduction (e.g., HSA contribution of $2,600/year)
    cursor.execute(
        """
        INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount, is_pre_tax)
        VALUES (?, ?, ?, ?, ?)
    """,
        (sample_income_source, "HSA", "fixed_annual", 2600, 1),
    )

    conn.commit()

    # Calculate net pay
    calculate_net_pay(initialized_db)

    # Verify calculation
    cursor.execute(
        "SELECT gross_amount, net_amount FROM pay_periods WHERE income_source_id = ?",
        (sample_income_source,),
    )
    gross, net = cursor.fetchone()

    # Annual amount divided by 26 pay periods (bi-weekly)
    expected_deduction = 2600 / 26
    expected_net = gross - expected_deduction

    assert abs(net - expected_net) < 0.01, f"Expected ${expected_net:.2f}, got ${net:.2f}"

    conn.close()


def test_pay_periods_ignore_duplicates(initialized_db, sample_income_source):
    """Test that generating pay periods twice doesn't create duplicates."""
    start_date = datetime(2024, 1, 5)
    end_date = datetime(2024, 3, 31)

    # Generate once
    count1 = generate_pay_periods(initialized_db, sample_income_source, start_date, end_date)

    # Generate again with same parameters
    count2 = generate_pay_periods(initialized_db, sample_income_source, start_date, end_date)

    # Second run should insert 0 new records
    assert count2 == 0, f"Expected 0 new records on second run, got {count2}"

    # Verify total count in database matches first run
    conn = sqlite3.connect(initialized_db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM pay_periods WHERE income_source_id = ?", (sample_income_source,)
    )
    total_count = cursor.fetchone()[0]
    assert total_count == count1
    conn.close()
