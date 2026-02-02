# Personal Budget App - Database Schema Design

## Overview
This schema supports zero-based budgeting with virtual funds, real account tracking, and flexible income/expense planning for a multi-person household.

**Database**: PostgreSQL 16
**Relationships**: Foreign keys with CASCADE/RESTRICT as appropriate
**Indexing**: Strategic indexes on frequently queried columns

---

## Schema Diagram (Entity Relationship)

```
users
  ↓ (1:N)
income_sources
  ↓ (1:N)
income_events ← budget_period_income (M:N) → budget_periods
                                                ↓ (1:N)
accounts ← account_transactions                budget_period_expenses
  ↑                                              ↓
  └─────────────────────────────────────────────┘

expense_categories
  ↓ (1:N)
expense_templates ← budget_period_expenses
                     ↓
                    funds ← fund_transactions
                             ↑
                    allocation_rules
```

---

## Table Definitions

### 1. users
**Purpose**: Household members who contribute income or have expenses

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_active (is_active)
);
```

**Sample Data**:
```
id | name  | email              | is_active
1  | Sarah | sarah@example.com  | TRUE
2  | Tom   | tom@example.com    | TRUE
```

---

### 2. accounts
**Purpose**: Real bank/financial accounts where money physically resides

```sql
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    account_type ENUM('checking', 'savings', 'money_market', 'investment', 'other') NOT NULL,
    institution VARCHAR(100),
    starting_balance DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    starting_balance_date DATE NOT NULL,
    current_balance DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_active (is_active),
    INDEX idx_type (account_type)
);
```

**Sample Data**:
```
id | name              | account_type | institution    | starting_balance | current_balance | is_active
1  | Joint Checking    | checking     | Chase Bank     | 5000.00          | 5500.00         | TRUE
2  | High-Yield Savings| savings      | Ally Bank      | 15000.00         | 18000.00        | TRUE
3  | Emergency Fund    | savings      | Marcus         | 10000.00         | 12000.00        | TRUE
```

**Notes**:
- `current_balance` is calculated: starting_balance + sum(income_events) - sum(expense transactions) + sum(transfers_in) - sum(transfers_out)
- Could be updated via trigger or application logic

---

### 3. income_sources
**Purpose**: Jobs, side hustles, or recurring income streams for each user

```sql
CREATE TABLE income_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    source_type ENUM('salary', 'hourly', 'freelance', 'investment', 'other') NOT NULL,
    amount_type ENUM('fixed', 'variable') NOT NULL DEFAULT 'fixed',
    frequency ENUM('weekly', 'bi-weekly', 'semi-monthly', 'monthly', 'quarterly', 'annual', 'one-time', 'irregular') NOT NULL,

    -- For fixed/salary income
    amount_per_period DECIMAL(12, 2),
    annual_amount DECIMAL(12, 2),

    -- Scheduling
    first_payment_date DATE,
    last_payment_date DATE,

    -- Which account does income deposit into?
    default_account_id INT,

    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (default_account_id) REFERENCES accounts(id) ON DELETE SET NULL,

    INDEX idx_user (user_id),
    INDEX idx_active (is_active),
    INDEX idx_frequency (frequency)
);
```

**Sample Data**:
```
id | user_id | name            | source_type | amount_type | frequency  | amount_per_period | annual_amount | default_account_id
1  | 1       | Sarah's Salary  | salary      | fixed       | bi-weekly  | 2500.00           | 65000.00      | 1
2  | 2       | Tom's Salary    | salary      | fixed       | bi-weekly  | 2300.00           | 59800.00      | 1
3  | 1       | Side Consulting | freelance   | variable    | irregular  | NULL              | NULL          | 1
```

---

### 4. income_events
**Purpose**: Specific instances of income (actual paychecks or planned income)

```sql
CREATE TABLE income_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    income_source_id INT NOT NULL,
    account_id INT NOT NULL,

    event_date DATE NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,

    event_status ENUM('planned', 'received', 'cancelled') DEFAULT 'planned',

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (income_source_id) REFERENCES income_sources(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE RESTRICT,

    UNIQUE KEY unique_income_event (income_source_id, event_date),
    INDEX idx_date (event_date),
    INDEX idx_status (event_status)
);
```

**Sample Data**:
```
id | income_source_id | account_id | event_date  | amount   | event_status
1  | 1                | 1          | 2026-01-03  | 2500.00  | planned
2  | 2                | 1          | 2026-01-03  | 2300.00  | planned
3  | 1                | 1          | 2026-01-17  | 2500.00  | planned
4  | 2                | 1          | 2026-01-17  | 2300.00  | planned
5  | 3                | 1          | 2026-01-15  | 500.00   | planned
```

**Notes**:
- Auto-generated based on income_source frequency and date range
- Can be manually added for irregular/one-time income
- Status tracks whether income is planned vs actually received

---

### 5. expense_categories
**Purpose**: Hierarchical categories for organizing expenses

```sql
CREATE TABLE expense_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_category_id INT,
    is_fixed BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (parent_category_id) REFERENCES expense_categories(id) ON DELETE SET NULL,

    UNIQUE KEY unique_category_name (name, parent_category_id),
    INDEX idx_parent (parent_category_id),
    INDEX idx_active (is_active)
);
```

**Sample Data**:
```
id | name              | parent_category_id | is_fixed | sort_order
1  | Housing           | NULL               | TRUE     | 1
2  | Mortgage/Rent     | 1                  | TRUE     | 1
3  | Utilities         | 1                  | FALSE    | 2
4  | Transportation    | NULL               | FALSE    | 2
5  | Car Payment       | 4                  | TRUE     | 1
6  | Gas               | 4                  | FALSE    | 2
7  | Food              | NULL               | FALSE    | 3
8  | Groceries         | 7                  | FALSE    | 1
9  | Dining Out        | 7                  | FALSE    | 2
```

---

### 6. expense_templates
**Purpose**: Reusable expense items (recurring expenses, typical amounts)

```sql
CREATE TABLE expense_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,

    expense_type ENUM('fixed_recurring', 'variable_recurring', 'one_time', 'fund_allocation') NOT NULL,
    frequency ENUM('weekly', 'bi-weekly', 'monthly', 'quarterly', 'annual', 'one-time') NOT NULL,

    typical_amount DECIMAL(12, 2),

    -- Which account is this paid from?
    default_account_id INT,

    -- Optional: which fund is this paid from?
    default_fund_id INT,

    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES expense_categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (default_account_id) REFERENCES accounts(id) ON DELETE SET NULL,
    FOREIGN KEY (default_fund_id) REFERENCES funds(id) ON DELETE SET NULL,

    INDEX idx_category (category_id),
    INDEX idx_type (expense_type),
    INDEX idx_active (is_active)
);
```

**Sample Data**:
```
id | name              | category_id | expense_type      | frequency | typical_amount | default_account_id
1  | Mortgage          | 2           | fixed_recurring   | monthly   | 2000.00        | 1
2  | Electric Bill     | 3           | variable_recurring| monthly   | 150.00         | 1
3  | Car Payment       | 5           | fixed_recurring   | monthly   | 450.00         | 1
4  | Groceries         | 8           | variable_recurring| monthly   | 600.00         | 1
5  | Gas               | 6           | variable_recurring| monthly   | 200.00         | 1
```

---

### 7. funds
**Purpose**: Virtual savings envelopes / goal-based funds

```sql
CREATE TABLE funds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    fund_type ENUM('savings_goal', 'sinking_fund', 'emergency', 'general') NOT NULL,

    target_amount DECIMAL(12, 2),
    current_balance DECIMAL(12, 2) NOT NULL DEFAULT 0.00,

    target_date DATE,

    -- Funds are virtual but "live" in a physical account
    primary_account_id INT,

    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (primary_account_id) REFERENCES accounts(id) ON DELETE SET NULL,

    INDEX idx_active (is_active),
    INDEX idx_type (fund_type)
);
```

**Sample Data**:
```
id | name                | fund_type     | target_amount | current_balance | target_date | primary_account_id
1  | Vacation Fund       | savings_goal  | 5000.00       | 2400.00         | 2026-07-01  | 2
2  | Car Replacement     | sinking_fund  | 20000.00      | 8500.00         | 2028-12-31  | 2
3  | Emergency Fund      | emergency     | 15000.00      | 12000.00        | NULL        | 3
4  | House Down Payment  | savings_goal  | 50000.00      | 18000.00        | 2027-06-01  | 2
5  | Christmas/Holidays  | sinking_fund  | 1200.00       | 600.00          | 2026-12-01  | 2
```

**Notes**:
- `current_balance` is calculated from fund_transactions
- Multiple funds can be in same physical account (virtual allocation)

---

### 8. fund_transactions
**Purpose**: Track all money movements in/out of funds

```sql
CREATE TABLE fund_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fund_id INT NOT NULL,
    transaction_date DATE NOT NULL,

    transaction_type ENUM('allocation', 'spend', 'transfer_in', 'transfer_out', 'adjustment') NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,

    -- If transfer, which fund was the other party?
    related_fund_id INT,

    -- If spend, link to the expense
    expense_id INT,

    -- If allocation, link to income event
    income_event_id INT,

    description VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (fund_id) REFERENCES funds(id) ON DELETE CASCADE,
    FOREIGN KEY (related_fund_id) REFERENCES funds(id) ON DELETE SET NULL,
    FOREIGN KEY (income_event_id) REFERENCES income_events(id) ON DELETE SET NULL,

    INDEX idx_fund (fund_id),
    INDEX idx_date (transaction_date),
    INDEX idx_type (transaction_type)
);
```

**Sample Data**:
```
id | fund_id | transaction_date | transaction_type | amount  | income_event_id | description
1  | 1       | 2026-01-03       | allocation       | 400.00  | 1               | January paycheck allocation
2  | 2       | 2026-01-03       | allocation       | 300.00  | 1               | Car fund contribution
3  | 3       | 2026-01-03       | allocation       | 300.00  | 1               | Emergency fund top-up
4  | 1       | 2026-01-15       | spend            | 500.00  | NULL            | Vacation planning expense
```

---

### 9. budget_periods
**Purpose**: Monthly budget plan (master record for each month)

```sql
CREATE TABLE budget_periods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL CHECK (month BETWEEN 1 AND 12),

    status ENUM('draft', 'active', 'closed') DEFAULT 'draft',

    total_planned_income DECIMAL(12, 2) DEFAULT 0.00,
    total_planned_expenses DECIMAL(12, 2) DEFAULT 0.00,
    total_fund_allocations DECIMAL(12, 2) DEFAULT 0.00,
    unallocated_amount DECIMAL(12, 2) DEFAULT 0.00,

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY unique_period (year, month),
    INDEX idx_year_month (year, month),
    INDEX idx_status (status)
);
```

**Sample Data**:
```
id | year | month | status | total_planned_income | total_planned_expenses | total_fund_allocations | unallocated_amount
1  | 2026 | 1     | active | 9800.00              | 7500.00                | 2000.00                | 300.00
2  | 2026 | 2     | draft  | 9600.00              | 7500.00                | 2000.00                | 100.00
```

**Notes**:
- Totals can be calculated/cached from related tables
- `unallocated_amount` = income - expenses - fund_allocations (should be zero for zero-based budgeting)

---

### 10. budget_period_income
**Purpose**: Link income events to budget periods (M:N relationship)

```sql
CREATE TABLE budget_period_income (
    id INT AUTO_INCREMENT PRIMARY KEY,
    budget_period_id INT NOT NULL,
    income_event_id INT NOT NULL,

    -- Allow override of income amount for "what-if" scenarios
    planned_amount DECIMAL(12, 2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (budget_period_id) REFERENCES budget_periods(id) ON DELETE CASCADE,
    FOREIGN KEY (income_event_id) REFERENCES income_events(id) ON DELETE CASCADE,

    UNIQUE KEY unique_budget_income (budget_period_id, income_event_id),
    INDEX idx_budget (budget_period_id),
    INDEX idx_income (income_event_id)
);
```

**Sample Data**:
```
id | budget_period_id | income_event_id | planned_amount
1  | 1                | 1               | 2500.00
2  | 1                | 2               | 2300.00
3  | 1                | 3               | 2500.00
4  | 1                | 4               | 2300.00
5  | 1                | 5               | 500.00
```

---

### 11. budget_period_expenses
**Purpose**: Planned expenses for a specific budget period

```sql
CREATE TABLE budget_period_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    budget_period_id INT NOT NULL,
    expense_template_id INT,
    category_id INT NOT NULL,

    name VARCHAR(100) NOT NULL,
    planned_amount DECIMAL(12, 2) NOT NULL,

    expense_type ENUM('fixed_recurring', 'variable_recurring', 'one_time', 'fund_allocation') NOT NULL,

    -- Which account will this be paid from?
    account_id INT,

    -- Optional: which fund will this be paid from?
    fund_id INT,

    due_date DATE,
    is_paid BOOLEAN DEFAULT FALSE,

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (budget_period_id) REFERENCES budget_periods(id) ON DELETE CASCADE,
    FOREIGN KEY (expense_template_id) REFERENCES expense_templates(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES expense_categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE SET NULL,
    FOREIGN KEY (fund_id) REFERENCES funds(id) ON DELETE SET NULL,

    INDEX idx_budget (budget_period_id),
    INDEX idx_template (expense_template_id),
    INDEX idx_category (category_id),
    INDEX idx_due_date (due_date)
);
```

**Sample Data**:
```
id | budget_period_id | expense_template_id | category_id | name          | planned_amount | expense_type        | account_id | fund_id
1  | 1                | 1                   | 2           | Mortgage      | 2000.00        | fixed_recurring     | 1          | NULL
2  | 1                | 2                   | 3           | Electric Bill | 150.00         | variable_recurring  | 1          | NULL
3  | 1                | 3                   | 5           | Car Payment   | 450.00         | fixed_recurring     | 1          | NULL
4  | 1                | 4                   | 8           | Groceries     | 600.00         | variable_recurring  | 1          | NULL
5  | 1                | NULL                | 7           | Vacation Exp  | 500.00         | one_time            | 1          | 1
```

---

### 12. allocation_rules
**Purpose**: Automatic allocation rules for income distribution

```sql
CREATE TABLE allocation_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rule_type ENUM('percentage', 'fixed_amount', 'remainder') NOT NULL,

    -- What triggers this rule?
    income_source_id INT,  -- NULL = applies to all income

    -- Where does money go?
    target_type ENUM('fund', 'expense_category', 'account') NOT NULL,
    target_id INT NOT NULL,

    -- How much?
    percentage DECIMAL(5, 2),  -- e.g., 10.00 for 10%
    fixed_amount DECIMAL(12, 2),

    priority INT DEFAULT 0,  -- Lower number = higher priority
    is_active BOOLEAN DEFAULT TRUE,

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (income_source_id) REFERENCES income_sources(id) ON DELETE CASCADE,

    INDEX idx_income_source (income_source_id),
    INDEX idx_active (is_active),
    INDEX idx_priority (priority)
);
```

**Sample Data**:
```
id | name                    | rule_type  | income_source_id | target_type | target_id | percentage | fixed_amount | priority
1  | 15% to Emergency Fund   | percentage | NULL             | fund        | 3         | 15.00      | NULL         | 1
2  | $400/mo to Vacation     | fixed_amt  | NULL             | fund        | 1         | NULL       | 400.00       | 2
3  | 10% to House Fund       | percentage | NULL             | fund        | 4         | 10.00      | NULL         | 3
4  | Remainder to Savings    | remainder  | NULL             | account     | 2         | NULL       | NULL         | 99
```

**Notes**:
- Rules are applied in priority order when allocating income
- `remainder` type gets whatever is left after all other allocations

---

### 13. budget_templates
**Purpose**: Reusable budget templates for quick month setup

```sql
CREATE TABLE budget_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_active (is_active)
);
```

**Sample Data**:
```
id | name             | description                      | is_default
1  | Standard Month   | Typical month without extras     | TRUE
2  | Summer Budget    | Higher utilities, vacation funds | FALSE
3  | Holiday Budget   | Extra spending for gifts, travel | FALSE
```

---

### 14. budget_template_items
**Purpose**: Line items in a budget template

```sql
CREATE TABLE budget_template_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL,
    expense_template_id INT NOT NULL,
    planned_amount DECIMAL(12, 2) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (template_id) REFERENCES budget_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (expense_template_id) REFERENCES expense_templates(id) ON DELETE CASCADE,

    UNIQUE KEY unique_template_expense (template_id, expense_template_id),
    INDEX idx_template (template_id)
);
```

---

### 15. account_transactions (Optional - for future transaction tracking)
**Purpose**: Record actual money movements in accounts (if tracking actuals later)

```sql
CREATE TABLE account_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type ENUM('income', 'expense', 'transfer_in', 'transfer_out', 'adjustment') NOT NULL,

    amount DECIMAL(12, 2) NOT NULL,

    -- Link to planned items if applicable
    income_event_id INT,
    budget_expense_id INT,

    -- For transfers
    related_account_id INT,

    description VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (income_event_id) REFERENCES income_events(id) ON DELETE SET NULL,
    FOREIGN KEY (budget_expense_id) REFERENCES budget_period_expenses(id) ON DELETE SET NULL,
    FOREIGN KEY (related_account_id) REFERENCES accounts(id) ON DELETE SET NULL,

    INDEX idx_account (account_id),
    INDEX idx_date (transaction_date),
    INDEX idx_type (transaction_type)
);
```

---

### 16. gas_fillups
**Purpose**: Track individual gas fill-ups for expense tracking and trend analysis

```sql
CREATE TABLE IF NOT EXISTS gas_fillups (
    id SERIAL PRIMARY KEY,
    fill_date DATE NOT NULL,
    gallons NUMERIC(8, 3) NOT NULL,
    price_per_gallon NUMERIC(6, 3) NOT NULL,
    total_cost NUMERIC(8, 2) NOT NULL,
    odometer INTEGER,
    station VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_gas_fillups_date (fill_date DESC)
);
```

**Sample Data**:
```
id | fill_date   | gallons | price_per_gallon | total_cost | odometer | station
1  | 2026-01-28  | 12.500  | 3.199            | 39.99      | 45230    | Shell - Main St
2  | 2026-01-21  | 11.800  | 3.249            | 38.34      | 44920    | Costco
3  | 2026-01-14  | 13.200  | 3.099            | 40.91      | 44610    | Shell - Main St
```

**Notes**:
- No user FK needed — personal household app, single-user model
- `odometer` is nullable; when two consecutive fill-ups both have readings, MPG = (odometer2 - odometer1) / gallons2
- `total_cost` stored explicitly (not computed) to match receipt totals and handle rounding

---

### 17. down_payment_accounts
**Purpose**: Simple tracking of savings accounts earmarked for a house down payment

```sql
CREATE TABLE IF NOT EXISTS down_payment_accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    balance NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data**:
```
id | name                | balance   | notes                    | updated_at
1  | High-Yield Savings  | 18000.00  | Ally Bank                | 2026-01-28
2  | Money Market         | 12000.00  | Marcus                   | 2026-01-28
3  | House Fund (Checking)| 5000.00  | Chase earmarked portion  | 2026-01-15
```

**Notes**:
- Deliberately simpler than the full `accounts` + `funds` schema — user requested "simple balance display"
- User manually updates balances when they check their accounts
- Grand total across all entries = total available for down payment
- If the full budget app schema is implemented later, this table can be migrated or replaced

---

## Key Queries

### Calculate Current Fund Balance
```sql
SELECT
    f.id,
    f.name,
    f.target_amount,
    COALESCE(SUM(
        CASE
            WHEN ft.transaction_type IN ('allocation', 'transfer_in', 'adjustment') THEN ft.amount
            WHEN ft.transaction_type IN ('spend', 'transfer_out') THEN -ft.amount
            ELSE 0
        END
    ), 0) as current_balance,
    f.target_date
FROM funds f
LEFT JOIN fund_transactions ft ON f.id = ft.fund_id
WHERE f.is_active = TRUE
GROUP BY f.id, f.name, f.target_amount, f.target_date;
```

### Monthly Budget Summary
```sql
SELECT
    bp.year,
    bp.month,
    SUM(COALESCE(bpi.planned_amount, ie.amount)) as total_income,
    SUM(bpe.planned_amount) as total_expenses,
    SUM(COALESCE(bpi.planned_amount, ie.amount)) - SUM(bpe.planned_amount) as net_amount
FROM budget_periods bp
LEFT JOIN budget_period_income bpi ON bp.id = bpi.budget_period_id
LEFT JOIN income_events ie ON bpi.income_event_id = ie.id
LEFT JOIN budget_period_expenses bpe ON bp.id = bpe.budget_period_id
WHERE bp.year = 2026 AND bp.month = 1
GROUP BY bp.year, bp.month;
```

### Income Events for Month
```sql
SELECT
    ie.event_date,
    u.name as user_name,
    is_src.name as income_source,
    ie.amount,
    a.name as account_name
FROM income_events ie
JOIN income_sources is_src ON ie.income_source_id = is_src.id
JOIN users u ON is_src.user_id = u.id
JOIN accounts a ON ie.account_id = a.id
WHERE YEAR(ie.event_date) = 2026
  AND MONTH(ie.event_date) = 1
ORDER BY ie.event_date;
```

### Expense Breakdown by Category
```sql
SELECT
    ec.name as category,
    SUM(bpe.planned_amount) as total_amount,
    COUNT(bpe.id) as expense_count
FROM budget_period_expenses bpe
JOIN expense_categories ec ON bpe.category_id = ec.id
JOIN budget_periods bp ON bpe.budget_period_id = bp.id
WHERE bp.year = 2026 AND bp.month = 1
GROUP BY ec.name
ORDER BY total_amount DESC;
```

---

## Indexes Summary

**Critical Indexes** (automatically created by constraints):
- Primary keys on all tables
- Foreign key indexes
- Unique constraints (e.g., budget_periods year+month)

**Performance Indexes**:
- `income_events.event_date` - date range queries
- `budget_periods.year, month` - period lookups
- `fund_transactions.fund_id, transaction_date` - balance calculations
- `expense_categories.parent_category_id` - hierarchy queries
- `allocation_rules.priority, is_active` - rule processing

---

## Data Integrity Considerations

1. **Cascading Deletes**: User deletion cascades to income_sources and their events
2. **Balance Calculations**: Fund and account balances calculated from transactions (not stored redundantly unless cached)
3. **Zero-Based Budget Validation**: Application logic ensures `income = expenses + fund_allocations`
4. **Date Validation**: Event dates should fall within budget period month
5. **Amount Validation**: All money amounts >= 0 (enforce in application or triggers)

---

## Migration from Current Schema

The existing prototype schema can be partially migrated:
- `users` → maps directly
- `income_sources` → maps with field additions
- `expense_categories` → maps directly
- Some tables are completely new (accounts, funds, budget_periods, etc.)

Migration strategy:
1. Create new schema alongside existing
2. Copy compatible data (users, categories)
3. Transform income_sources and pay_periods → income_sources + income_events
4. Discard old expense/deduction structure (was prototype)
5. Start fresh with new budget_periods and fund structures

---

## Future Enhancements

Possible schema additions for future features:
- **Recurring transactions automation**: Add scheduling metadata
- **Budget variance tracking**: Add actual_amount fields to expenses
- **User authentication**: Add password_hash, session tokens to users
- **Shared budgets**: Add permissions table for multi-household
- **Audit logging**: Add audit_log table for all changes
- **Notifications**: Add reminders and alerts table

---

## Schema Version Control

**Version**: 1.0.0
**Created**: 2026-01-08
**Updated**: 2026-01-10 (switched to PostgreSQL)
**Database**: PostgreSQL 16

Schema changes should be tracked in migration files (e.g., Alembic, Flyway, or custom migration scripts).
