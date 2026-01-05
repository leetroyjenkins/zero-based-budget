#!/usr/bin/env python3
"""
Database initialization script for personal budget tracker.
Creates the SQLite database schema for household budget management.
"""

import os
import sqlite3
from datetime import datetime, timedelta


def init_database(db_path="budget.db"):
    """Initialize the budget database with required tables."""

    # Check if database already exists
    db_exists = os.path.exists(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create income_sources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            annual_salary REAL NOT NULL,
            pay_frequency TEXT NOT NULL CHECK(pay_frequency IN ('weekly', 'bi-weekly', 'semi-monthly', 'monthly')),
            first_pay_date DATE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Create paycheck_deductions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paycheck_deductions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            income_source_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            calculation_type TEXT NOT NULL CHECK(calculation_type IN ('percentage', 'fixed_per_paycheck', 'fixed_annual')),
            amount REAL NOT NULL,
            is_pre_tax BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (income_source_id) REFERENCES income_sources(id)
        )
    """)

    # Create pay_periods table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pay_periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            income_source_id INTEGER NOT NULL,
            pay_date DATE NOT NULL,
            gross_amount REAL NOT NULL,
            net_amount REAL,
            year INTEGER NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (income_source_id) REFERENCES income_sources(id),
            UNIQUE(income_source_id, pay_date)
        )
    """)

    # Create expense_categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_fixed BOOLEAN DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create monthly_expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
            planned_amount REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category_id, year, month),
            FOREIGN KEY (category_id) REFERENCES expense_categories(id)
        )
    """)

    # Create savings_goals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            target_date DATE,
            is_active BOOLEAN DEFAULT 1,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create budget_periods table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, month)
        )
    """)

    # Insert default data if this is a new database
    if not db_exists:
        # Default expense categories
        default_categories = [
            ("Housing (Rent/Mortgage)", 1, "Monthly housing payment"),
            ("Utilities", 1, "Electric, water, gas, internet"),
            ("Groceries", 0, "Food and household items"),
            ("Transportation", 0, "Gas, car maintenance, public transit"),
            ("Insurance", 1, "Car, home, life insurance"),
            ("Healthcare", 0, "Medical expenses, prescriptions"),
            ("Debt Payments", 1, "Credit cards, loans"),
            ("Entertainment", 0, "Dining out, movies, hobbies"),
            ("Clothing", 0, "Apparel and accessories"),
            ("Personal Care", 0, "Haircuts, toiletries"),
            ("Subscriptions", 1, "Streaming services, memberships"),
            ("Savings Transfer", 1, "Monthly savings contribution"),
            ("Emergency Fund", 0, "Emergency savings"),
            ("Miscellaneous", 0, "Other expenses"),
        ]

        cursor.executemany(
            "INSERT INTO expense_categories (name, is_fixed, description) VALUES (?, ?, ?)",
            default_categories,
        )

        print("Default expense categories added.")

    conn.commit()
    conn.close()

    if db_exists:
        print(f"Database '{db_path}' already exists. Schema verified.")
    else:
        print(f"Database '{db_path}' created successfully!")
        print("\nNext steps:")
        print("1. Add users (you and your wife)")
        print("2. Add income sources with pay dates")
        print("3. Add paycheck deductions (taxes, benefits, etc.)")
        print("4. Generate pay periods for the year")
        print("5. Set monthly expense budgets")
        print("6. Create savings goals")


def generate_pay_periods(
    db_path="budget.db", income_source_id=None, start_date=None, end_date=None
):
    """
    Generate pay periods for an income source.

    Args:
        db_path: Path to the database
        income_source_id: ID of the income source
        start_date: Start date (datetime object or 'YYYY-MM-DD' string)
        end_date: End date (datetime object or 'YYYY-MM-DD' string)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get income source details
    cursor.execute(
        """
        SELECT annual_salary, pay_frequency, first_pay_date
        FROM income_sources
        WHERE id = ?
    """,
        (income_source_id,),
    )

    result = cursor.fetchone()
    if not result:
        print(f"Income source {income_source_id} not found.")
        conn.close()
        return

    annual_salary, pay_frequency, first_pay_date = result

    # Convert string dates to datetime
    if isinstance(first_pay_date, str):
        first_pay_date = datetime.strptime(first_pay_date, "%Y-%m-%d")
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Calculate gross amount per paycheck
    if pay_frequency == "weekly":
        paychecks_per_year = 52
        days_between = 7
    elif pay_frequency == "bi-weekly":
        paychecks_per_year = 26
        days_between = 14
    elif pay_frequency == "semi-monthly":
        paychecks_per_year = 24
        days_between = None  # Special handling needed
    elif pay_frequency == "monthly":
        paychecks_per_year = 12
        days_between = None  # Special handling needed

    gross_per_paycheck = annual_salary / paychecks_per_year

    # Generate pay dates
    current_date = first_pay_date
    pay_periods = []

    while current_date <= end_date:
        if current_date >= start_date:
            pay_periods.append(
                (
                    income_source_id,
                    current_date.strftime("%Y-%m-%d"),
                    gross_per_paycheck,
                    current_date.year,
                )
            )

        # Calculate next pay date
        if days_between:
            current_date += timedelta(days=days_between)
        elif pay_frequency == "semi-monthly":
            # 1st and 15th of month (simplified)
            if current_date.day == 1:
                current_date = current_date.replace(day=15)
            else:
                next_month = current_date.month + 1 if current_date.month < 12 else 1
                next_year = current_date.year if current_date.month < 12 else current_date.year + 1
                current_date = current_date.replace(year=next_year, month=next_month, day=1)
        elif pay_frequency == "monthly":
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year if current_date.month < 12 else current_date.year + 1
            current_date = current_date.replace(year=next_year, month=next_month)

    # Insert pay periods
    cursor.executemany(
        """
        INSERT OR IGNORE INTO pay_periods (income_source_id, pay_date, gross_amount, year)
        VALUES (?, ?, ?, ?)
    """,
        pay_periods,
    )

    conn.commit()
    count = cursor.rowcount
    conn.close()

    print(f"Generated {count} pay periods for income source {income_source_id}")
    return count


def calculate_net_pay(db_path="budget.db", pay_period_id=None):
    """
    Calculate net pay for a pay period based on deductions.

    Args:
        db_path: Path to the database
        pay_period_id: ID of the pay period (if None, calculates for all)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get pay periods to calculate
    if pay_period_id:
        cursor.execute(
            """
            SELECT id, income_source_id, gross_amount
            FROM pay_periods
            WHERE id = ?
        """,
            (pay_period_id,),
        )
        pay_periods = cursor.fetchall()
    else:
        cursor.execute("""
            SELECT id, income_source_id, gross_amount
            FROM pay_periods
            WHERE net_amount IS NULL
        """)
        pay_periods = cursor.fetchall()

    for period_id, income_source_id, gross_amount in pay_periods:
        # Get deductions for this income source
        cursor.execute(
            """
            SELECT name, calculation_type, amount, is_pre_tax
            FROM paycheck_deductions
            WHERE income_source_id = ? AND is_active = 1
        """,
            (income_source_id,),
        )

        deductions = cursor.fetchall()

        # Get pay frequency for annual deduction calculations
        cursor.execute("SELECT pay_frequency FROM income_sources WHERE id = ?", (income_source_id,))
        pay_frequency = cursor.fetchone()[0]

        if pay_frequency == "bi-weekly":
            paychecks_per_year = 26
        elif pay_frequency == "weekly":
            paychecks_per_year = 52
        elif pay_frequency == "semi-monthly":
            paychecks_per_year = 24
        else:  # monthly
            paychecks_per_year = 12

        # Calculate deductions
        total_pre_tax = 0
        total_post_tax = 0
        taxable_income = gross_amount

        for _, calc_type, amount, is_pre_tax in deductions:
            if calc_type == "percentage":
                deduction = gross_amount * (amount / 100)
            elif calc_type == "fixed_per_paycheck":
                deduction = amount
            elif calc_type == "fixed_annual":
                deduction = amount / paychecks_per_year
            else:
                deduction = 0

            if is_pre_tax:
                total_pre_tax += deduction
                taxable_income -= deduction
            else:
                total_post_tax += deduction

        net_amount = gross_amount - total_pre_tax - total_post_tax

        # Update pay period with net amount
        cursor.execute(
            """
            UPDATE pay_periods
            SET net_amount = ?
            WHERE id = ?
        """,
            (net_amount, period_id),
        )

    conn.commit()
    count = len(pay_periods)
    conn.close()

    print(f"Calculated net pay for {count} pay periods")
    return count


if __name__ == "__main__":
    init_database()
