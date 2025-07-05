```markdown
## Module: loans.py

### Class: Loan
This class represents a loan object within the personal banking platform.

#### Attributes:
- `loan_id: int` - A unique identifier for each loan.
- `amount: float` - The initial amount requested for the loan.
- `term: int` - The term of the loan in months.
- `interest_rate: float` - The annual interest rate for the loan.
- `status: str` - The current status of the loan (`pending`, `active`, `paid`).
- `start_date: date` - The date when the loan was approved.
- `repayments: list` - A list of tuples containing repayment records (date, amount).
- `balance: float` - The remaining balance of the loan.
- `interest_paid: float` - The total interest paid so far.
- `principal_paid: float` - The total principal paid so far.

#### Methods:

- `__init__(self, amount: float, term: int, interest_rate: float)`
  - Initializes a new loan object with the specified parameters. Sets the initial status to `pending`.

- `approve_loan(self)`
  - Approves a pending loan, setting the status to `active` and initializing the start date and balance.

- `make_repayment(self, payment_date: date, amount: float)`
  - Makes a repayment towards the loan. Adjusts the balance, calculates the interest and principal paid. Raises an error if the loan is not `active` or if the repayment is greater than the remaining balance.

- `get_status(self) -> str`
  - Returns the current status of the loan (`pending`, `active`, `paid`).

- `generate_amortization_schedule(self) -> list`
  - Returns a list representing the amortization schedule with month-by-month breakdowns of principal and interest.

- `get_total_paid(self) -> dict`
  - Returns a dictionary with the total amount paid, total interest paid, and amount remaining.

- `get_next_due(self) -> dict`
  - Provides details of the next due payment, including due date and expected payment amount.

### Helper Functions

- `get_current_date() -> date`
  - Simulates and returns the system's current date.

### Test Implementation

#### Test 1: Test Loan Approval and Activation
- Create a loan with specific amount, term, and interest rate.
- Check if the loan status is `pending`.
- Approve the loan.
- Verify the loan status is changed to `active`.

#### Test 2: Test Partial Repayment
- Make a partial repayment on an active loan.
- Verify the updated balance, interest paid, and principal paid.

#### Test 3: Test Repayment on Fully Paid Loan
- Attempt to repay a fully paid loan.
- Verify that an error is raised.

This design provides a comprehensive structure for implementing a simple loan management system, covering all essential functional requirements while abstracting detailed computations inside the class methods. The test cases are formulated to verify core functionalities robustly.  
```