from datetime import date, timedelta

def get_current_date():
    """Simulates and returns the system's current date."""
    return date.today()

class Loan:
    """Represents a loan object within the personal banking platform."""
    
    _next_id = 1  # Class variable to keep track of next loan ID
    
    def __init__(self, amount: float, term: int, interest_rate: float):
        """Initializes a new loan object with the specified parameters.
        
        Args:
            amount: The initial amount requested for the loan.
            term: The term of the loan in months.
            interest_rate: The annual interest rate for the loan (e.g., 5.0 for 5%).
        """
        self.loan_id = Loan._next_id
        Loan._next_id += 1
        
        self.amount = amount
        self.term = term
        self.interest_rate = interest_rate
        self.status = 'pending'
        self.start_date = None
        self.repayments = []
        self.balance = amount
        self.interest_paid = 0.0
        self.principal_paid = 0.0
        
    def approve_loan(self):
        """Approves a pending loan, setting the status to active 
        and initializing the start date and balance."""
        if self.status != 'pending':
            raise ValueError(f"Cannot approve loan with status: {self.status}")
            
        self.status = 'active'
        self.start_date = get_current_date()
        self.balance = self.amount
        
    def make_repayment(self, payment_date: date, amount: float):
        """Makes a repayment towards the loan.
        
        Args:
            payment_date: The date of the payment.
            amount: The amount being paid.
            
        Raises:
            ValueError: If the loan is not active or payment exceeds balance.
        """
        if self.status != 'active':
            raise ValueError(f"Cannot make repayment on loan with status: {self.status}")
            
        # Calculate monthly interest rate
        monthly_rate = self.interest_rate / 100 / 12
        
        # Calculate interest for this payment
        interest_portion = self.balance * monthly_rate
        
        # Calculate the total amount due (balance + interest)
        total_due = self.balance + interest_portion
        
        if amount > total_due:
            raise ValueError(f"Payment amount (${amount:.2f}) exceeds total due (${total_due:.2f})")
        
        # Calculate principal for this payment
        principal_portion = min(amount - interest_portion, self.balance)
        
        # If interest exceeds payment amount, all goes to interest
        if interest_portion > amount:
            interest_portion = amount
            principal_portion = 0
        
        # Update loan state
        self.interest_paid += interest_portion
        self.principal_paid += principal_portion
        self.balance -= principal_portion
        
        # Record the repayment
        self.repayments.append((payment_date, amount))
        
        # Check if loan is fully paid
        if abs(self.balance) < 0.01:  # Using a small threshold to account for floating-point errors
            self.balance = 0
            self.status = 'paid'
            
    def get_status(self) -> str:
        """Returns the current status of the loan."""
        return self.status
    
    def generate_amortization_schedule(self) -> list:
        """Returns a list representing the amortization schedule."""
        if self.status == 'pending':
            raise ValueError("Cannot generate amortization schedule for a pending loan")
            
        schedule = []
        monthly_rate = self.interest_rate / 100 / 12
        
        # Calculate fixed monthly payment using the loan formula
        # P = A * r * (1 + r)^n / ((1 + r)^n - 1)
        # where P is payment, A is amount, r is monthly rate, n is term
        if monthly_rate > 0 and self.term > 1:
            monthly_payment = self.amount * monthly_rate * (1 + monthly_rate) ** self.term / ((1 + monthly_rate) ** self.term - 1)
        else:
            monthly_payment = self.amount / self.term
            
        remaining_balance = self.amount
        current_date = self.start_date
        
        for month in range(1, self.term + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            
            # Adjust for final payment
            if month == self.term:
                principal_payment = remaining_balance
                monthly_payment = principal_payment + interest_payment
                
            remaining_balance -= principal_payment
            
            # Ensure we don't have negative balance due to rounding
            if remaining_balance < 0:
                remaining_balance = 0
                
            payment_date = date(current_date.year + (current_date.month + month - 1) // 12,
                               ((current_date.month + month - 1) % 12) + 1,
                               min(current_date.day, 28))  # Using 28 to avoid month/day issues
            
            schedule.append({
                'month': month,
                'date': payment_date,
                'payment': monthly_payment,
                'principal': principal_payment,
                'interest': interest_payment,
                'remaining_balance': remaining_balance
            })
            
        return schedule
    
    def get_total_paid(self) -> dict:
        """Returns a dictionary with the total amount paid and amount remaining."""
        total_paid = sum(amount for _, amount in self.repayments)
        
        return {
            'total_paid': total_paid,
            'interest_paid': self.interest_paid,
            'principal_paid': self.principal_paid,
            'remaining_balance': self.balance
        }
    
    def get_next_due(self) -> dict:
        """Provides details of the next due payment."""
        if self.status != 'active':
            raise ValueError(f"Cannot get next due date for loan with status: {self.status}")
            
        # Generate amortization schedule
        schedule = self.generate_amortization_schedule()
        
        # Find the next payment based on repayments made
        payments_made = len(self.repayments)
        
        if payments_made >= len(schedule):
            return {"message": "All scheduled payments have been made"}
        
        next_payment = schedule[payments_made]
        
        return {
            'due_date': next_payment['date'],
            'payment_amount': next_payment['payment'],
            'principal': next_payment['principal'],
            'interest': next_payment['interest']
        }
        
    def get_current_payment_amount(self):
        """Returns the current payment amount including interest."""
        if self.status != 'active':
            raise ValueError(f"Cannot get payment amount for loan with status: {self.status}")
            
        monthly_rate = self.interest_rate / 100 / 12
        interest_portion = self.balance * monthly_rate
        return self.balance + interest_portion

# Test Cases
if __name__ == '__main__':
    # Test 1: Test Loan Approval and Activation
    print("\n=== Test 1: Loan Approval and Activation ===")
    loan1 = Loan(amount=10000, term=12, interest_rate=5.0)
    print(f"Initial loan status: {loan1.get_status()}")
    loan1.approve_loan()
    print(f"Loan status after approval: {loan1.get_status()}")
    
    # Test 2: Test Partial Repayment
    print("\n=== Test 2: Partial Repayment ===")
    loan2 = Loan(amount=10000, term=12, interest_rate=5.0)
    loan2.approve_loan()
    
    # Get the amortization schedule to know how much to pay
    schedule = loan2.generate_amortization_schedule()
    monthly_payment = schedule[0]['payment']
    print(f"Monthly payment amount: ${monthly_payment:.2f}")
    
    # Make a partial payment (half of the expected monthly payment)
    partial_payment = monthly_payment / 2
    payment_date = get_current_date() + timedelta(days=30)  # One month later
    loan2.make_repayment(payment_date, partial_payment)
    
    # Check loan state after partial payment
    loan_state = loan2.get_total_paid()
    print(f"Total paid: ${loan_state['total_paid']:.2f}")
    print(f"Interest paid: ${loan_state['interest_paid']:.2f}")
    print(f"Principal paid: ${loan_state['principal_paid']:.2f}")
    print(f"Remaining balance: ${loan_state['remaining_balance']:.2f}")
    
    # Test 3: Test Repayment on Fully Paid Loan
    print("\n=== Test 3: Repayment on Fully Paid Loan ===")
    loan3 = Loan(amount=1000, term=1, interest_rate=5.0)
    loan3.approve_loan()
    
    # Calculate total due including interest
    monthly_rate = loan3.interest_rate / 100 / 12
    interest = loan3.balance * monthly_rate
    total_due = loan3.balance + interest
    
    # Pay off the loan completely
    payment_date = get_current_date() + timedelta(days=15)
    print(f"Making full payment of ${total_due:.2f}")
    loan3.make_repayment(payment_date, total_due)
    
    # Verify the loan is marked as paid
    print(f"Loan status after full payment: {loan3.get_status()}")
    print(f"Remaining balance: ${loan3.balance:.2f}")
    
    # Try to make another payment
    try:
        loan3.make_repayment(payment_date + timedelta(days=15), 100)
        print("Error: Was able to make a payment on a paid loan!")
    except ValueError as e:
        print(f"Success: Caught expected error - {e}")