# Personal Budget Manager - Implementation Plan

## Current Status
- ✅ Basic database schema created with users, income, pay_periods, taxes, deductions, and expenses tables
- ✅ Initial Streamlit app with basic CRUD operations
- ✅ Test infrastructure set up (pytest, coverage, pre-commit hooks)
- ✅ Basic income and expense tracking working

## Planned Features (from notes.md)

### 1. Income Source as Slowly Changing Dimension (SCD)
**Goal**: Track historical changes to income sources (e.g., pay raises, job changes)

**Implementation Steps**:
- Add SCD Type 2 columns to income table:
  - `effective_from` (date)
  - `effective_to` (date, nullable)
  - `is_current` (boolean)
- Update income insertion logic to handle versioning
- Create UI for viewing income history
- Add tests for SCD behavior

### 2. Clean Up UI - Remove Unnecessary Columns
**Goal**: Hide row numbers and database IDs from user-facing views

**Implementation Steps**:
- Review all dataframe displays in app.py
- Remove index display from dataframes
- Remove ID columns from user views (keep for internal operations)
- Update tests to verify UI changes

### 3. Annual Income View
**Goal**: Show a full year's income at a glance

**Implementation Steps**:
- Create annual income summary query
- Add year selector to UI
- Display monthly breakdown with totals
- Add visualization (chart/graph)
- Add tests for annual calculations

### 4. Dashboard: Account Balances
**Goal**: Show current balances across different accounts

**Implementation Steps**:
- Create accounts table if needed
- Add account balance tracking
- Create dashboard view showing all accounts
- Add visualization for account overview
- Add tests for account calculations

### 5. Dashboard: Special Funds with Forecasting
**Goal**: Track special savings funds (rainy day, down payment, clothing, etc.) with future projections

**Implementation Steps**:
- Create funds table
- Add fund allocation logic
- Implement forecasting algorithm based on income/expense patterns
- Create dashboard with current and projected fund balances
- Add date range selector for forecasts
- Add visualization for fund growth over time
- Add tests for forecasting logic

### 6. Dashboard: Income vs Expenses Summary
**Goal**: Comparative view of income vs expenses with flexible time slicing

**Implementation Steps**:
- Create aggregation queries for income and expenses
- Add time period selector (month/quarter/year)
- Create comparison visualization
- Add drill-down capability
- Calculate net savings/deficit
- Add tests for aggregations

## Next Steps
1. Prioritize which feature to implement first
2. Create detailed technical design for chosen feature
3. Implement with TDD approach (tests first)
4. Update README with new functionality

## Technical Considerations
- All new code should use type hints
- Follow PEP 8 style guidelines
- Run pytest after each change
- Update documentation as features are added
- Consider database migrations for schema changes
