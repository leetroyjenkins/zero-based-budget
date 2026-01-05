# Personal Budget Manager

A Streamlit-based budget management application for tracking household finances on a Raspberry Pi.

## Features

- **Bi-weekly Pay Periods**: Automatically generates pay dates based on your pay schedule
- **Paycheck Deductions**: Track taxes, healthcare, 401k, and other deductions (pre-tax and post-tax)
- **Monthly Expense Budgets**: Plan expenses by category for any month/year
- **Savings Goals**: Set and track progress toward savings targets
- **Multi-user Support**: Track combined finances for household members
- **Automatic Net Pay Calculation**: Calculates take-home pay based on deductions

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python init_db.py
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Usage Guide

### 1. Initial Setup
- Navigate to the **Setup** page
- Add yourself and your spouse as users
- Add income sources (jobs) with annual salary, pay frequency, and first pay date

### 2. Configure Deductions
- Go to **Income & Deductions**
- Add paycheck deductions like:
  - Federal Tax (percentage)
  - State Tax (percentage)
  - Social Security (percentage)
  - Medicare (percentage)
  - 401k contributions (percentage or fixed, pre-tax)
  - Health insurance (fixed per paycheck)
  - HSA contributions (pre-tax)
- View sample paycheck calculation to verify

### 3. Generate Pay Periods
- Go to **Pay Periods**
- Select income source and date range (e.g., entire year)
- Click "Generate Pay Periods" to create all pay dates
- Net pay is automatically calculated based on deductions

### 4. Set Monthly Budgets
- Go to **Expenses**
- Select month and year
- Add planned expenses for each category
- Use "Copy from previous month" for recurring expenses

### 5. Create Savings Goals
- Go to **Savings Goals**
- Add goals with target amounts and dates
- Update progress as you save

### 6. Monitor Dashboard
- View the **Dashboard** for an overview:
  - Monthly income vs expenses
  - Available savings
  - Savings goals progress
  - Expense breakdown

## Database Schema

- **users**: Household members
- **income_sources**: Jobs with salary and pay schedule
- **paycheck_deductions**: Taxes and benefits
- **pay_periods**: Generated pay dates with calculated net amounts
- **expense_categories**: Budget categories
- **monthly_expenses**: Planned spending by month
- **savings_goals**: Savings targets and progress
- **budget_periods**: Monthly budget tracking

## Running on Raspberry Pi

This app is designed to run on a Raspberry Pi:

1. Install Python 3.7+ on your Raspberry Pi
2. Follow installation steps above
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. Access the app in your browser at `http://localhost:8501` or `http://<raspberry-pi-ip>:8501`

## Tips

- **Deduction Types**:
  - `percentage`: Deducts a % of gross pay (e.g., 15% for federal tax)
  - `fixed_per_paycheck`: Fixed amount each paycheck (e.g., $200 for health insurance)
  - `fixed_annual`: Annual amount divided across paychecks (e.g., $2,400/year HSA)

- **Pre-tax vs Post-tax**: Mark deductions like 401k and HSA as pre-tax to reduce taxable income

- **Pay Frequencies**: Supports weekly, bi-weekly, semi-monthly (1st & 15th), and monthly

- **Multi-year**: Generate pay periods for any year to plan future budgets
