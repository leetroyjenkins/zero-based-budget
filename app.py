#!/usr/bin/env python3
"""
Streamlit app for personal budget management.
Allows users to populate and manage the budget database.
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from init_db import init_database, generate_pay_periods, calculate_net_pay

# Page config
st.set_page_config(
    page_title="Personal Budget Manager",
    page_icon="💰",
    layout="wide"
)

DB_PATH = 'budget.db'

# Initialize database if needed
init_database(DB_PATH)


def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)


def main():
    st.title("💰 Personal Budget Manager")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Setup", "Income & Deductions", "Expenses", "Savings Goals", "Pay Periods"]
    )

    if page == "Dashboard":
        show_dashboard()
    elif page == "Setup":
        show_setup()
    elif page == "Income & Deductions":
        show_income_deductions()
    elif page == "Expenses":
        show_expenses()
    elif page == "Savings Goals":
        show_savings_goals()
    elif page == "Pay Periods":
        show_pay_periods()


def show_dashboard():
    """Display overview dashboard."""
    st.header("Budget Dashboard")

    conn = get_db_connection()

    # Get current month/year
    current_year = datetime.now().year
    current_month = datetime.now().month

    col1, col2, col3 = st.columns(3)

    # Monthly income
    with col1:
        st.subheader("Monthly Income")
        query = """
            SELECT SUM(net_amount) as total
            FROM pay_periods
            WHERE year = ? AND strftime('%m', pay_date) = ?
        """
        result = pd.read_sql_query(query, conn, params=(current_year, f"{current_month:02d}"))
        monthly_income = result['total'].iloc[0] if result['total'].iloc[0] else 0
        st.metric("Net Income (Current Month)", f"${monthly_income:,.2f}")

    # Monthly expenses
    with col2:
        st.subheader("Monthly Expenses")
        query = """
            SELECT SUM(planned_amount) as total
            FROM monthly_expenses
            WHERE year = ? AND month = ?
        """
        result = pd.read_sql_query(query, conn, params=(current_year, current_month))
        monthly_expenses = result['total'].iloc[0] if result['total'].iloc[0] else 0
        st.metric("Planned Expenses", f"${monthly_expenses:,.2f}")

    # Savings
    with col3:
        st.subheader("Savings")
        remaining = monthly_income - monthly_expenses
        st.metric("Available for Savings", f"${remaining:,.2f}")

    # Active savings goals
    st.subheader("Active Savings Goals")
    query = """
        SELECT name, target_amount, current_amount, target_date,
               ROUND((current_amount * 100.0 / target_amount), 2) as progress_pct
        FROM savings_goals
        WHERE is_active = 1
        ORDER BY target_date
    """
    goals_df = pd.read_sql_query(query, conn)

    if not goals_df.empty:
        for _, goal in goals_df.iterrows():
            progress = goal['progress_pct'] if goal['progress_pct'] else 0
            st.write(f"**{goal['name']}**")
            st.progress(min(progress / 100, 1.0))
            st.write(f"${goal['current_amount']:,.2f} / ${goal['target_amount']:,.2f} ({progress:.1f}%)")
            if goal['target_date']:
                st.write(f"Target: {goal['target_date']}")
            st.write("---")
    else:
        st.info("No active savings goals. Add some in the Savings Goals section.")

    # Expense breakdown
    st.subheader(f"Expense Breakdown - {datetime(current_year, current_month, 1).strftime('%B %Y')}")
    query = """
        SELECT ec.name, me.planned_amount
        FROM monthly_expenses me
        JOIN expense_categories ec ON me.category_id = ec.id
        WHERE me.year = ? AND me.month = ?
        ORDER BY me.planned_amount DESC
    """
    expenses_df = pd.read_sql_query(query, conn, params=(current_year, current_month))

    if not expenses_df.empty:
        st.bar_chart(expenses_df.set_index('name'))
    else:
        st.info("No expenses planned for this month. Set them up in the Expenses section.")

    conn.close()


def show_setup():
    """Initial setup page for users and income sources."""
    st.header("Initial Setup")

    conn = get_db_connection()

    # Users section
    st.subheader("1. Add Users")
    st.write("Add yourself and your spouse to the system.")

    # Display existing users
    users_df = pd.read_sql_query("SELECT * FROM users WHERE is_active = 1", conn)
    if not users_df.empty:
        st.dataframe(users_df[['id', 'name', 'created_at']], use_container_width=True)

    with st.form("add_user_form"):
        user_name = st.text_input("Name")
        submit = st.form_submit_button("Add User")

        if submit and user_name:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name) VALUES (?)", (user_name,))
            conn.commit()
            st.success(f"Added user: {user_name}")
            st.rerun()

    st.write("---")

    # Income sources section
    st.subheader("2. Add Income Sources")
    st.write("Add jobs/income sources for each user.")

    if users_df.empty:
        st.warning("Please add users first before adding income sources.")
    else:
        # Display existing income sources
        income_df = pd.read_sql_query("""
            SELECT is_.id, u.name as user, is_.name as income_source,
                   is_.annual_salary, is_.pay_frequency, is_.first_pay_date
            FROM income_sources is_
            JOIN users u ON is_.user_id = u.id
            WHERE is_.is_active = 1
        """, conn)

        if not income_df.empty:
            st.dataframe(income_df, use_container_width=True)

        with st.form("add_income_form"):
            col1, col2 = st.columns(2)

            with col1:
                user_id = st.selectbox(
                    "User",
                    options=users_df['id'].tolist(),
                    format_func=lambda x: users_df[users_df['id'] == x]['name'].iloc[0]
                )
                income_name = st.text_input("Income Source Name (e.g., 'Main Job')")
                annual_salary = st.number_input("Annual Salary ($)", min_value=0.0, step=1000.0)

            with col2:
                pay_frequency = st.selectbox(
                    "Pay Frequency",
                    options=['bi-weekly', 'weekly', 'semi-monthly', 'monthly']
                )
                first_pay_date = st.date_input("First Pay Date (or next pay date)")

            submit_income = st.form_submit_button("Add Income Source")

            if submit_income and income_name and annual_salary > 0:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO income_sources (user_id, name, annual_salary, pay_frequency, first_pay_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, income_name, annual_salary, pay_frequency, first_pay_date.strftime('%Y-%m-%d')))
                conn.commit()
                st.success(f"Added income source: {income_name}")
                st.rerun()

    conn.close()


def show_income_deductions():
    """Manage income sources and paycheck deductions."""
    st.header("Income & Deductions")

    conn = get_db_connection()

    # Get income sources
    income_df = pd.read_sql_query("""
        SELECT is_.id, u.name as user, is_.name as income_source,
               is_.annual_salary, is_.pay_frequency
        FROM income_sources is_
        JOIN users u ON is_.user_id = u.id
        WHERE is_.is_active = 1
    """, conn)

    if income_df.empty:
        st.warning("No income sources found. Please add them in the Setup section.")
        conn.close()
        return

    # Select income source
    selected_income = st.selectbox(
        "Select Income Source",
        options=income_df['id'].tolist(),
        format_func=lambda x: f"{income_df[income_df['id'] == x]['user'].iloc[0]} - {income_df[income_df['id'] == x]['income_source'].iloc[0]}"
    )

    st.write("---")

    # Display existing deductions
    st.subheader("Current Deductions")
    deductions_df = pd.read_sql_query("""
        SELECT id, name, calculation_type, amount, is_pre_tax, is_active
        FROM paycheck_deductions
        WHERE income_source_id = ?
        ORDER BY is_pre_tax DESC, name
    """, conn, params=(selected_income,))

    if not deductions_df.empty:
        # Format for display
        display_df = deductions_df.copy()
        display_df['is_pre_tax'] = display_df['is_pre_tax'].map({1: 'Yes', 0: 'No'})
        display_df['is_active'] = display_df['is_active'].map({1: 'Active', 0: 'Inactive'})
        st.dataframe(display_df, use_container_width=True)

        # Delete deduction
        with st.expander("Delete Deduction"):
            deduction_to_delete = st.selectbox(
                "Select deduction to delete",
                options=deductions_df['id'].tolist(),
                format_func=lambda x: deductions_df[deductions_df['id'] == x]['name'].iloc[0]
            )
            if st.button("Delete Deduction"):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM paycheck_deductions WHERE id = ?", (deduction_to_delete,))
                conn.commit()
                st.success("Deduction deleted")
                st.rerun()
    else:
        st.info("No deductions added yet.")

    st.write("---")

    # Add new deduction
    st.subheader("Add New Deduction")

    with st.form("add_deduction_form"):
        col1, col2 = st.columns(2)

        with col1:
            deduction_name = st.text_input("Deduction Name (e.g., 'Federal Tax', '401k')")
            calc_type = st.selectbox(
                "Calculation Type",
                options=['percentage', 'fixed_per_paycheck', 'fixed_annual'],
                format_func=lambda x: {
                    'percentage': 'Percentage of Gross',
                    'fixed_per_paycheck': 'Fixed Amount Per Paycheck',
                    'fixed_annual': 'Fixed Annual Amount'
                }[x]
            )
            amount = st.number_input(
                "Amount (% or $)",
                min_value=0.0,
                step=0.01,
                help="Enter percentage (e.g., 15 for 15%) or dollar amount"
            )

        with col2:
            is_pre_tax = st.checkbox(
                "Pre-tax Deduction",
                help="Check if this reduces taxable income (e.g., 401k, HSA)"
            )

        submit_deduction = st.form_submit_button("Add Deduction")

        if submit_deduction and deduction_name and amount > 0:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO paycheck_deductions (income_source_id, name, calculation_type, amount, is_pre_tax)
                VALUES (?, ?, ?, ?, ?)
            """, (selected_income, deduction_name, calc_type, amount, 1 if is_pre_tax else 0))
            conn.commit()
            st.success(f"Added deduction: {deduction_name}")
            st.rerun()

    # Sample paycheck calculation
    st.write("---")
    st.subheader("Sample Paycheck Calculation")

    income_info = income_df[income_df['id'] == selected_income].iloc[0]
    annual_salary = income_info['annual_salary']
    pay_frequency = income_info['pay_frequency']

    if pay_frequency == 'bi-weekly':
        paychecks_per_year = 26
    elif pay_frequency == 'weekly':
        paychecks_per_year = 52
    elif pay_frequency == 'semi-monthly':
        paychecks_per_year = 24
    else:
        paychecks_per_year = 12

    gross_per_paycheck = annual_salary / paychecks_per_year

    st.write(f"**Gross Pay Per Paycheck:** ${gross_per_paycheck:,.2f}")

    if not deductions_df.empty:
        total_pre_tax = 0
        total_post_tax = 0

        st.write("**Deductions:**")
        for _, ded in deductions_df[deductions_df['is_active'] == 1].iterrows():
            if ded['calculation_type'] == 'percentage':
                ded_amount = gross_per_paycheck * (ded['amount'] / 100)
            elif ded['calculation_type'] == 'fixed_per_paycheck':
                ded_amount = ded['amount']
            else:  # fixed_annual
                ded_amount = ded['amount'] / paychecks_per_year

            if ded['is_pre_tax']:
                total_pre_tax += ded_amount
                st.write(f"- {ded['name']} (Pre-tax): ${ded_amount:,.2f}")
            else:
                total_post_tax += ded_amount
                st.write(f"- {ded['name']} (Post-tax): ${ded_amount:,.2f}")

        net_pay = gross_per_paycheck - total_pre_tax - total_post_tax

        st.write(f"**Total Pre-tax Deductions:** ${total_pre_tax:,.2f}")
        st.write(f"**Total Post-tax Deductions:** ${total_post_tax:,.2f}")
        st.write(f"**NET PAY:** ${net_pay:,.2f}")

    conn.close()


def show_expenses():
    """Manage monthly expense budgets."""
    st.header("Monthly Expense Budgets")

    conn = get_db_connection()

    # Select month/year
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.number_input("Year", min_value=2020, max_value=2050, value=datetime.now().year)
    with col2:
        selected_month = st.selectbox("Month", options=list(range(1, 13)),
                                     format_func=lambda x: datetime(2000, x, 1).strftime('%B'))

    st.write("---")

    # Get expense categories
    categories_df = pd.read_sql_query("SELECT * FROM expense_categories ORDER BY name", conn)

    # Get existing monthly expenses
    existing_expenses = pd.read_sql_query("""
        SELECT me.id, ec.name, me.planned_amount, me.notes
        FROM monthly_expenses me
        JOIN expense_categories ec ON me.category_id = ec.id
        WHERE me.year = ? AND me.month = ?
        ORDER BY ec.name
    """, conn, params=(selected_year, selected_month))

    st.subheader(f"Budget for {datetime(selected_year, selected_month, 1).strftime('%B %Y')}")

    if not existing_expenses.empty:
        st.dataframe(existing_expenses, use_container_width=True)
        total = existing_expenses['planned_amount'].sum()
        st.metric("Total Planned Expenses", f"${total:,.2f}")
    else:
        st.info("No expenses set for this month.")

    st.write("---")

    # Add/Update expense
    st.subheader("Add or Update Expense")

    with st.form("expense_form"):
        category_id = st.selectbox(
            "Category",
            options=categories_df['id'].tolist(),
            format_func=lambda x: categories_df[categories_df['id'] == x]['name'].iloc[0]
        )

        planned_amount = st.number_input("Planned Amount ($)", min_value=0.0, step=10.0)
        notes = st.text_area("Notes (optional)")

        submit = st.form_submit_button("Save Expense")

        if submit and planned_amount >= 0:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO monthly_expenses (category_id, year, month, planned_amount, notes)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(category_id, year, month)
                DO UPDATE SET planned_amount = ?, notes = ?
            """, (category_id, selected_year, selected_month, planned_amount, notes, planned_amount, notes))
            conn.commit()
            st.success("Expense saved")
            st.rerun()

    # Quick copy from previous month
    st.write("---")
    st.subheader("Quick Actions")

    prev_month = selected_month - 1 if selected_month > 1 else 12
    prev_year = selected_year if selected_month > 1 else selected_year - 1

    if st.button(f"Copy expenses from {datetime(prev_year, prev_month, 1).strftime('%B %Y')}"):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO monthly_expenses (category_id, year, month, planned_amount, notes)
            SELECT category_id, ?, ?, planned_amount, notes
            FROM monthly_expenses
            WHERE year = ? AND month = ?
        """, (selected_year, selected_month, prev_year, prev_month))
        conn.commit()
        st.success(f"Copied expenses from previous month ({cursor.rowcount} items)")
        st.rerun()

    conn.close()


def show_savings_goals():
    """Manage savings goals."""
    st.header("Savings Goals")

    conn = get_db_connection()

    # Display existing goals
    goals_df = pd.read_sql_query("""
        SELECT id, name, target_amount, current_amount, target_date, is_active, notes,
               ROUND((current_amount * 100.0 / target_amount), 2) as progress_pct
        FROM savings_goals
        ORDER BY is_active DESC, target_date
    """, conn)

    if not goals_df.empty:
        st.subheader("Your Savings Goals")

        for _, goal in goals_df.iterrows():
            with st.expander(f"{goal['name']} - {'Active' if goal['is_active'] else 'Inactive'}"):
                progress = goal['progress_pct'] if goal['progress_pct'] else 0
                st.progress(min(progress / 100, 1.0))

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Target", f"${goal['target_amount']:,.2f}")
                with col2:
                    st.metric("Current", f"${goal['current_amount']:,.2f}")
                with col3:
                    st.metric("Progress", f"{progress:.1f}%")

                if goal['target_date']:
                    st.write(f"**Target Date:** {goal['target_date']}")
                if goal['notes']:
                    st.write(f"**Notes:** {goal['notes']}")

                # Update progress
                with st.form(f"update_goal_{goal['id']}"):
                    new_amount = st.number_input(
                        "Update Current Amount ($)",
                        min_value=0.0,
                        value=float(goal['current_amount']),
                        step=10.0
                    )
                    col_a, col_b = st.columns(2)
                    with col_a:
                        update_submit = st.form_submit_button("Update Amount")
                    with col_b:
                        toggle_active = st.form_submit_button(
                            "Deactivate" if goal['is_active'] else "Activate"
                        )

                    if update_submit:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE savings_goals SET current_amount = ? WHERE id = ?
                        """, (new_amount, goal['id']))
                        conn.commit()
                        st.success("Updated savings amount")
                        st.rerun()

                    if toggle_active:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE savings_goals SET is_active = ? WHERE id = ?
                        """, (0 if goal['is_active'] else 1, goal['id']))
                        conn.commit()
                        st.success("Updated goal status")
                        st.rerun()

    st.write("---")

    # Add new goal
    st.subheader("Add New Savings Goal")

    with st.form("add_goal_form"):
        col1, col2 = st.columns(2)

        with col1:
            goal_name = st.text_input("Goal Name (e.g., 'Emergency Fund', 'Vacation')")
            target_amount = st.number_input("Target Amount ($)", min_value=0.0, step=100.0)
            current_amount = st.number_input("Current Amount ($)", min_value=0.0, step=100.0, value=0.0)

        with col2:
            target_date = st.date_input("Target Date (optional)")
            notes = st.text_area("Notes (optional)")

        submit = st.form_submit_button("Add Savings Goal")

        if submit and goal_name and target_amount > 0:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO savings_goals (name, target_amount, current_amount, target_date, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (goal_name, target_amount, current_amount, target_date.strftime('%Y-%m-%d'), notes))
            conn.commit()
            st.success(f"Added savings goal: {goal_name}")
            st.rerun()

    conn.close()


def show_pay_periods():
    """View and generate pay periods."""
    st.header("Pay Periods")

    conn = get_db_connection()

    # Get income sources
    income_df = pd.read_sql_query("""
        SELECT is_.id, u.name as user, is_.name as income_source
        FROM income_sources is_
        JOIN users u ON is_.user_id = u.id
        WHERE is_.is_active = 1
    """, conn)

    if income_df.empty:
        st.warning("No income sources found. Please add them in the Setup section.")
        conn.close()
        return

    # Generate pay periods
    st.subheader("Generate Pay Periods")

    with st.form("generate_periods_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            income_source_id = st.selectbox(
                "Income Source",
                options=income_df['id'].tolist(),
                format_func=lambda x: f"{income_df[income_df['id'] == x]['user'].iloc[0]} - {income_df[income_df['id'] == x]['income_source'].iloc[0]}"
            )

        with col2:
            start_date = st.date_input("Start Date", value=datetime(datetime.now().year, 1, 1))

        with col3:
            end_date = st.date_input("End Date", value=datetime(datetime.now().year, 12, 31))

        generate = st.form_submit_button("Generate Pay Periods")

        if generate:
            count = generate_pay_periods(
                DB_PATH,
                income_source_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            # Calculate net pay
            calculate_net_pay(DB_PATH)

            st.success(f"Generated {count} pay periods and calculated net pay")
            st.rerun()

    st.write("---")

    # View pay periods
    st.subheader("View Pay Periods")

    selected_income = st.selectbox(
        "Select Income Source to View",
        options=income_df['id'].tolist(),
        format_func=lambda x: f"{income_df[income_df['id'] == x]['user'].iloc[0]} - {income_df[income_df['id'] == x]['income_source'].iloc[0]}"
    )

    selected_year = st.number_input("Year", min_value=2020, max_value=2050, value=datetime.now().year)

    periods_df = pd.read_sql_query("""
        SELECT pay_date, gross_amount, net_amount
        FROM pay_periods
        WHERE income_source_id = ? AND year = ?
        ORDER BY pay_date
    """, conn, params=(selected_income, selected_year))

    if not periods_df.empty:
        st.dataframe(periods_df, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pay Periods", len(periods_df))
        with col2:
            st.metric("Total Gross", f"${periods_df['gross_amount'].sum():,.2f}")
        with col3:
            total_net = periods_df['net_amount'].sum() if periods_df['net_amount'].notna().any() else 0
            st.metric("Total Net", f"${total_net:,.2f}")
    else:
        st.info("No pay periods found. Generate them above.")

    conn.close()


if __name__ == '__main__':
    main()
