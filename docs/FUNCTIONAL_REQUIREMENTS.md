# Personal Budget App - Functional Requirements

## Overview
A planning and forecasting budget application for a household of 2 people to manage income allocation, expense planning, and savings goals across multiple funds and accounts. This is **NOT a transaction tracker** - it's a forward-looking budgeting tool.

## Core Concept
**Zero-Based Budgeting with Virtual Funds**: All income is allocated to specific purposes (expenses, funds/envelopes, savings goals). Money physically exists in real bank accounts but is virtually allocated to different funds (vacation, car, house down payment, etc.).

---

## User Requirements

### UR1: Multi-Person Household
- **Requirement**: Support 2 people (couple) managing budget together
- **Details**:
  - Each person may have separate income sources
  - Combined view of household finances
  - May have individual and shared expenses
- **Future**: Could expand to more household members or separate login views

### UR2: Access and Platform
- **Local Network**: Primary access via local network on Raspberry Pi
- **Multi-Device**: Accessible from desktop, tablet, mobile devices
- **Future**: Remote access via VPN or secure tunnel
- **Mobile-Responsive**: Must work well on phones and tablets

---

## Income Management

### IN1: Income Sources
- **Fixed Salary**: Regular paychecks with consistent amounts
- **Multiple Sources**: Each person can have multiple income sources (primary job, side hustle)
- **Variable/Irregular**: Support for freelance, commission, seasonal income
- **One-Time Income**: Tax refunds, bonuses, gifts, windfalls
- **Frequency Options**: Weekly, bi-weekly, semi-monthly, monthly, quarterly, annual, one-time

### IN2: Income Allocation
- **Manual Allocation**: Each month, manually decide how to allocate income to categories, funds, and expenses
- **Template-Based**: Create budget templates that can be applied to months
- **Automatic Allocation**: Define rules (e.g., "10% of paycheck to vacation fund") that auto-allocate
- **Flexible Adjustments**: Ability to adjust allocations month-by-month as needed

### IN3: Income Timing
- **Scheduled Income**: Define when income arrives (pay dates)
- **Multi-Period Planning**: See both monthly and annual income projections
- **Pay Period Tracking**: Know which paychecks fall in which months

---

## Expense Management

### EX1: Expense Types

#### Fixed Recurring Expenses
- Same amount every period
- Examples: Rent, mortgage, car payment, insurance, subscriptions
- Auto-populate each month based on template

#### Variable Recurring Expenses
- Amount varies but occurs regularly
- Examples: Groceries, utilities, gas, dining out
- Can set planned amount that adjusts month-to-month

#### Planned One-Time Expenses
- Large purchases or non-recurring costs
- Examples: Car repair, vacation, new appliance, medical bills
- Scheduled for specific months
- May be funded from savings funds

#### Sinking Funds / Savings Goals
- Regular monthly contributions toward future expenses
- Examples: Annual insurance premium, property taxes, holiday gifts
- Tracks balance and target amount

### EX2: Expense Categories
- User-defined categories (e.g., Housing, Transportation, Food, Entertainment)
- Hierarchical categories possible (e.g., Food → Groceries, Dining Out)
- Expenses assigned to categories for reporting
- Default category templates provided but fully customizable

### EX3: Expense Planning Period
- **Monthly Budgets**: Primary planning in monthly buckets
- **Annual View**: See yearly totals and projections
- **Month-to-Month Variation**: Different amounts in different months as needed
- **Copy Template**: Ability to copy previous month's budget as starting point

---

## Funds & Envelopes

### FU1: Virtual Funds (Cash Envelopes)
- **Concept**: Virtual allocations of money toward specific purposes
- **Examples**:
  - Vacation Fund
  - Car Replacement Fund
  - House Down Payment Fund
  - Emergency Fund
  - Christmas/Holiday Fund
  - Home Maintenance Fund

### FU2: Fund Operations

#### Allocate Income to Fund
- Take money from incoming income and assign to fund
- Can allocate specific dollar amount or percentage
- Multiple funds can receive allocations from single paycheck

#### Spend from Fund
- Record planned expense that will come out of specific fund
- Reduces fund balance
- Expense still categorized (e.g., "Vacation Expense from Vacation Fund")

#### Transfer Between Funds
- Move money from one fund to another
- Example: Realized house fund is overfunded, move some to car fund

#### Track Fund Targets/Goals
- Set target amount for each fund
- See current balance vs target
- See percentage complete
- Estimate completion date based on allocation rate

### FU3: Fund Balance Tracking
- See current balance in each fund
- Historical view of fund growth over time
- Total of all fund balances = portion of savings allocated to funds

---

## Accounts Management

### AC1: Real Bank Accounts
- **Requirement**: Track actual bank/financial accounts where money physically resides
- **Account Types**:
  - Checking accounts
  - Savings accounts
  - Money market accounts
  - Investment accounts (optional, may exclude for MVP)

### AC2: Account Operations
- **Starting Balance**: Set initial balance when account is added
- **Allocations**: Income arrives into specific accounts
- **Expenses**: Expenses paid from specific accounts
- **Transfers**: Move money between accounts
- **Balance Tracking**: Current balance = starting + income - expenses + transfers

### AC3: Accounts vs Funds Relationship
- **Physical vs Virtual**:
  - Accounts = where money physically is (bank accounts)
  - Funds = what money is for (vacation, car, emergency)
- **Example**:
  - $10,000 in Savings Account (physical)
  - Allocated as: $3k vacation fund, $4k car fund, $3k emergency fund (virtual)
- **Unallocated Money**: Money in accounts not assigned to funds = available for allocation

---

## Budget Planning Workflow

### WF1: Monthly Budget Creation
1. **Select Month/Year**: Choose which month to budget
2. **Income Entry**: Add expected income for the month (from recurring sources + any one-time)
3. **Expense Planning**:
   - Add/adjust fixed recurring expenses
   - Plan variable expenses (set amounts)
   - Add any one-time expenses for that month
4. **Fund Allocation**: Decide how much to allocate to each fund
5. **Balance Check**: Verify income = expenses + fund allocations + savings (zero-based)
6. **Save Budget**: Store budget plan for the month

### WF2: Template Application
- Create "Master Budget Template" with typical month's income/expenses
- Apply template to new month
- Adjust as needed for month-specific variations
- Multiple templates possible (e.g., "Summer Budget" vs "Winter Budget")

### WF3: Automatic Allocation Rules
- Define rules like:
  - "Allocate 15% of each paycheck to emergency fund"
  - "Put $200/month into vacation fund"
  - "After all expenses, remaining goes to house fund"
- Rules can be applied automatically or as suggestions
- Override/adjust allocations manually as needed

---

## Reporting & Visualization

### RP1: Budget Summary View
- **Income vs Expenses**: Total income - total expenses = amount for savings/funds
- **Monthly Snapshot**:
  - Total income this month
  - Total expenses this month
  - Amount allocated to funds
  - Net savings rate
- **Annual Projection**: Extrapolate current month's budget to annual numbers

### RP2: Fund Balances Dashboard
- **Current State**: Show all funds with current balances
- **Visual Progress**: Progress bars or gauges for funds with targets
- **Fund Details**:
  - Current balance
  - Target amount (if applicable)
  - Monthly contribution rate
  - Estimated time to goal
- **Total Available Savings**: Sum of all fund balances

### RP3: Account Balances View
- List all real accounts with current balances
- Show recent activity (income, expenses, transfers)
- Total net worth = sum of all account balances

### RP4: Cash Flow Projection (Future Enhancement)
- Timeline showing when income arrives and expenses are due
- Running balance projection
- Identify potential shortfalls
- Plan timing of large expenses

### RP5: Category Breakdown
- Pie chart or bar chart of planned expenses by category
- Compare planned amounts across categories
- See category spending as % of total budget

---

## Key Scenarios

### Scenario 1: Regular Monthly Budgeting
Sarah and Tom get paid bi-weekly. They want to plan next month's budget:
1. Open app, select "November 2026"
2. System shows 2 of Sarah's paychecks + 2 of Tom's paychecks = $8,000 total income
3. Copy last month's budget as starting point
4. Adjust: Add $500 for holiday shopping, reduce dining out by $100
5. Allocate: $1,000 to savings funds ($400 vacation, $300 car, $300 emergency)
6. Verify: Income ($8,000) = Expenses ($6,500) + Funds ($1,000) + Unallocated savings ($500) ✓
7. Save budget for November

### Scenario 2: Planning a Large Purchase
They want to take a $3,000 vacation in 6 months:
1. Create "Vacation Fund" with $3,000 target
2. Set up automatic allocation: $500/month to vacation fund
3. Each month, budget allocates $500 to fund
4. Dashboard shows progress: "$2,500 / $3,000 (83%) - On track for June"
5. When vacation month arrives, create $3,000 "Vacation Expense" from Vacation Fund

### Scenario 3: Unexpected Expense
Car needs $800 repair in March:
1. Check Emergency Fund balance: $2,000 ✓
2. Add one-time expense to March budget: "Car Repair - $800"
3. Set expense to be paid from Emergency Fund
4. Emergency Fund reduces to $1,200
5. Increase future monthly allocations to replenish fund

### Scenario 4: Income Change
Tom gets a raise starting in April:
1. Update Tom's income source: increase annual salary
2. System recalculates paychecks starting April
3. Create allocation rule: "Put 50% of raise toward house fund"
4. April+ budgets automatically show increased income
5. Adjust fund allocations to take advantage of extra income

---

## Data Model Concepts

### Core Entities
1. **Users**: Household members (Sarah, Tom)
2. **Accounts**: Real bank accounts where money resides
3. **Income Sources**: Jobs, side hustles, etc. (linked to users)
4. **Income Events**: Specific paychecks or income receipts (scheduled/projected)
5. **Expense Categories**: Groupings for expenses (Housing, Food, Transportation)
6. **Expense Items**: Specific planned expenses (Rent, Groceries, Gas)
7. **Funds**: Virtual envelopes/savings buckets (Vacation, Car, Emergency)
8. **Budget Periods**: Monthly budget plans linking income and expenses
9. **Fund Transactions**: Allocations, spending, transfers affecting fund balances
10. **Allocation Rules**: Templates and auto-allocation logic

### Key Relationships
- User → has many → Income Sources
- Income Source → generates → Income Events (paychecks)
- Income Event → allocated to → Expense Items + Funds + Accounts
- Expense Item → belongs to → Category
- Expense Item → paid from → Account (and optionally Fund)
- Fund → has many → Fund Transactions
- Account → has many → Income Events, Expense Items, Transfers
- Budget Period → contains → Income Events, Expense Items, Fund Allocations

---

## Non-Functional Requirements

### NF1: Performance
- Page load times < 2 seconds on local network
- Support 2-3 concurrent users without slowdown
- Handle 10+ years of budget data efficiently

### NF2: Data Persistence & Backup
- All data stored in database (MariaDB)
- Daily automated backups
- Easy export to CSV/Excel for external analysis

### NF3: Usability
- Intuitive interface, minimal learning curve
- Responsive design works on all device sizes
- Clear visual feedback on budget balance (income allocated = income available)
- Helpful error messages and validation

### NF4: Security
- HTTPS encryption for all connections
- Secure session management
- No plain-text password storage (if authentication added)
- Database credentials secured

### NF5: Maintainability
- Clean, modular code structure
- Documentation for setup and deployment
- CI/CD pipeline for easy updates
- Version control with Git

---

## Out of Scope (MVP)

### Not Included in Initial Version:
- ❌ Transaction tracking (actual expenses vs planned)
- ❌ Bank account integration / automatic import
- ❌ Bill payment functionality
- ❌ Investment tracking and portfolio management
- ❌ Debt payoff calculators
- ❌ Receipt scanning / OCR
- ❌ Mobile native apps (iOS/Android) - web only
- ❌ Multi-household/tenant support
- ❌ Advanced analytics / machine learning predictions
- ❌ Shared budgets with separate login views
- ❌ Budget comparisons across time periods
- ❌ What-if scenario modeling

### Future Enhancements (Post-MVP):
- Cash flow timeline visualization
- Budget variance analysis (if actual tracking added later)
- Recurring transaction auto-generation improvements
- Advanced reporting and charts
- Budget sharing / export features
- Integration with external tools
- User authentication and permissions

---

## Success Criteria

The MVP is successful when:
1. ✅ Sarah and Tom can create monthly budgets for 12 months
2. ✅ They can define income sources and see projected paychecks
3. ✅ They can plan expenses in categories with recurring and one-time items
4. ✅ They can create and track multiple funds (vacation, car, emergency, house)
5. ✅ They can allocate income to expenses and funds, achieving zero-based budget
6. ✅ They can see fund balances and progress toward goals
7. ✅ They can track real account balances and see where money physically is
8. ✅ Dashboard provides clear summary: income vs expenses, fund balances, savings rate
9. ✅ Application accessible from any device on local network via HTTPS
10. ✅ Budget templates can be created and applied to speed up monthly planning

---

## Questions for Future Clarification

1. **Historical Data**: How far back should budget history be retained? Forever?
2. **Budget Versions**: If you change a past month's budget, should it keep history or overwrite?
3. **Fund Interest**: Do funds earn interest if in savings accounts? Track separately?
4. **Shared vs Individual**: Should some expenses/funds be marked as individual vs household?
5. **Notifications**: Want reminders (e.g., "Time to create next month's budget")?
6. **Import/Export**: What formats for data export? CSV, Excel, JSON?
7. **Account Reconciliation**: Need to reconcile planned balances with actual bank statements?
