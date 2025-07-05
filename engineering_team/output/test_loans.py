import unittest
from unittest.mock import patch
from datetime import date, timedelta
from loans import Loan, get_current_date  # Import the class and function we're testing

class TestLoans(unittest.TestCase):
    
    def test_loan_initialization(self):
        """Test that a loan is properly initialized with default values."""
        loan = Loan(amount=10000, term=12, interest_rate=5.0)
        
        # Check initial values
        self.assertEqual(loan.amount, 10000)
        self.assertEqual(loan.term, 12)
        self.assertEqual(loan.interest_rate, 5.0)
        self.assertEqual(loan.status, 'pending')
        self.assertIsNone(loan.start_date)
        self.assertEqual(loan.balance, 10000)
        self.assertEqual(loan.interest_paid, 0.0)
        self.assertEqual(loan.principal_paid, 0.0)
        self.assertEqual(len(loan.repayments), 0)
    
    def test_loan_id_assignment(self):
        """Test that loan IDs are unique and auto-incrementing."""
        # Reset the loan ID counter for consistent testing
        original_next_id = Loan._next_id
        Loan._next_id = 1
        
        loan1 = Loan(1000, 12, 5.0)
        loan2 = Loan(2000, 24, 6.0)
        
        self.assertEqual(loan1.loan_id, 1)
        self.assertEqual(loan2.loan_id, 2)
        
        # Restore the original next_id value
        Loan._next_id = original_next_id
    
    @patch('loans.get_current_date')
    def test_approve_loan(self, mock_get_current_date):
        """Test approving a loan."""
        test_date = date(2023, 1, 15)
        mock_get_current_date.return_value = test_date
        
        loan = Loan(10000, 12, 5.0)
        self.assertEqual(loan.status, 'pending')
        
        loan.approve_loan()
        
        self.assertEqual(loan.status, 'active')
        self.assertEqual(loan.start_date, test_date)
        self.assertEqual(loan.balance, 10000)  # Balance should be the initial amount
    
    def test_approve_non_pending_loan(self):
        """Test that approving a non-pending loan raises an error."""
        loan = Loan(10000, 12, 5.0)
        loan.status = 'active'  # Change status manually for testing
        
        with self.assertRaises(ValueError):
            loan.approve_loan()
    
    @patch('loans.get_current_date')
    def test_make_repayment(self, mock_get_current_date):
        """Test making a repayment on an active loan."""
        test_date = date(2023, 1, 15)
        mock_get_current_date.return_value = test_date
        
        loan = Loan(10000, 12, 5.0)
        loan.approve_loan()
        
        payment_date = test_date + timedelta(days=30)
        payment_amount = 1000  # More than the interest but less than full payment
        
        loan.make_repayment(payment_date, payment_amount)
        
        # Check that repayment was recorded
        self.assertEqual(len(loan.repayments), 1)
        self.assertEqual(loan.repayments[0], (payment_date, payment_amount))
        
        # Check that the loan state was updated
        self.assertLess(loan.balance, 10000)  # Balance should be reduced
        self.assertGreater(loan.interest_paid, 0)  # Some interest should be paid
        self.assertGreater(loan.principal_paid, 0)  # Some principal should be paid
    
    def test_make_repayment_on_non_active_loan(self):
        """Test that making a repayment on a non-active loan raises an error."""
        loan = Loan(10000, 12, 5.0)
        # Loan is still in 'pending' status
        
        with self.assertRaises(ValueError):
            loan.make_repayment(date.today(), 1000)
    
    def test_make_excessive_repayment(self):
        """Test that making a repayment exceeding the total due raises an error."""
        loan = Loan(10000, 12, 5.0)
        loan.approve_loan()
        
        # Calculate total due (balance + interest)
        monthly_rate = loan.interest_rate / 100 / 12
        interest = loan.balance * monthly_rate
        total_due = loan.balance + interest
        
        # Try to pay more than the total due
        with self.assertRaises(ValueError):
            loan.make_repayment(date.today(), total_due + 100)
    
    def test_full_repayment(self):
        """Test making a full repayment that completes the loan."""
        loan = Loan(10000, 12, 5.0)
        loan.approve_loan()
        
        # Calculate total due (balance + interest)
        monthly_rate = loan.interest_rate / 100 / 12
        interest = loan.balance * monthly_rate
        total_due = loan.balance + interest
        
        # Make the full payment
        loan.make_repayment(date.today(), total_due)
        
        # Check that the loan is marked as paid
        self.assertEqual(loan.status, 'paid')
        self.assertEqual(loan.balance, 0)  # Balance should be zero
    
    def test_get_status(self):
        """Test getting the loan status."""
        loan = Loan(10000, 12, 5.0)
        self.assertEqual(loan.get_status(), 'pending')
        
        loan.status = 'active'  # Change status manually for testing
        self.assertEqual(loan.get_status(), 'active')
    
    def test_generate_amortization_schedule_pending_loan(self):
        """Test that generating an amortization schedule for a pending loan raises an error."""
        loan = Loan(10000, 12, 5.0)
        # Loan is still in 'pending' status
        
        with self.assertRaises(ValueError):
            loan.generate_amortization_schedule()
    
    @patch('loans.get_current_date')
    def test_generate_amortization_schedule(self, mock_get_current_date):
        """Test generating an amortization schedule for an active loan."""
        test_date = date(2023, 1, 15)
        mock_get_current_date.return_value = test_date
        
        loan = Loan(10000, 12, 5.0)
        loan.approve_loan()
        
        schedule = loan.generate_amortization_schedule()
        
        # Check that the schedule has the correct number of entries
        self.assertEqual(len(schedule), 12)
        
        # Check the first payment
        first_payment = schedule[0]
        self.assertEqual(first_payment['month'], 1)
        
        # Check that the final payment results in zero balance
        last_payment = schedule[-1]
        self.assertAlmostEqual(last_payment['remaining_balance'], 0, places=2)
        
        # Check that the total payments equal the loan amount plus interest
        total_payments = sum(payment['payment'] for payment in schedule)
        self.assertGreater(total_payments, loan.amount)  # Total should exceed the principal
    
    def test_generate_amortization_schedule_zero_interest(self):
        """Test generating an amortization schedule for a loan with zero interest."""
        loan = Loan(10000, 12, 0.0)
        loan.approve_loan()
        
        schedule = loan.generate_amortization_schedule()
        
        # Check that each payment is equal (no interest)
        payment_amount = schedule[0]['payment']
        for payment in schedule:
            self.assertAlmostEqual(payment['payment'], payment_amount, places=2)
        
        # Check that the total payments equal the loan amount
        total_payments = sum(payment['payment'] for payment in schedule)
        self.assertAlmostEqual(total_payments, loan.amount, places=2)
    
    def test_get_total_paid(self):
        """Test getting the total amount paid on a loan."""
        loan = Loan(10000, 12, 5.0)
        loan.approve_loan()
        
        # Make some repayments
        loan.make_repayment(date.today(), 500)
        loan.make_repayment(date.today() + timedelta(days=30), 500)
        
        total_paid_info = loan.get_total_paid()
        
        self.assertEqual(total_paid_info['total_paid'], 1000)  # 500 + 500
        self.assertGreater(total_paid_info['interest_paid'], 0)  # Some interest should be paid
        self.assertGreater(total_paid_info['principal_paid'], 0)  # Some principal should be paid
        self.assertLess(total_paid_info['remaining_balance'], 10000)  # Balance should be reduced
    
    def test_get_next_due_non_active_loan(self):
        """Test that getting the next due payment for a non-active loan raises an error."""
        loan = Loan(10000, 12, 5.0)
        # Loan is still in 'pending' status
        
        with self.assertRaises(ValueError):
            loan.get_next_due()
    
    @patch('loans.get_current_date')
    def test_get_next_due(self, mock_get_current_date):
        """Test getting the next due payment for an active loan."""
        test_date = date(2023, 1, 15)
        mock_get_current_date.return_value = test_date
        
        loan = Loan(10000, 12, 5.0)
        loan.approve_loan()
        
        next_due = loan.get_next_due()
        
        # Check that next due has the expected fields
        self.assertIn('due_date', next_due)
        self.assertIn('payment_amount', next_due)
        self.assertIn('principal', next_due)
        self.assertIn('interest', next_due)
        
        # Make a payment and check that the next due is updated
        loan.make_repayment(date.today(), next_due['payment_amount'])
        
        next_due_after_payment = loan.get_next_due()
        self.assertNotEqual(next_due['due_date'], next_due_after_payment['due_date'])
    
    def test_get_next_due_all_paid(self):
        """Test getting the next due payment when all payments are made."""
        loan = Loan(1000, 1, 5.0)  # Small loan with just one payment
        loan.approve_loan()
        
        # Calculate total due (balance + interest)
        monthly_rate = loan.interest_rate / 100 / 12
        interest = loan.balance * monthly_rate
        total_due = loan.balance + interest
        
        # Make the full payment
        loan.make_repayment(date.today(), total_due)
        
        # Get next due, which should indicate all payments are made
        next_due = loan.get_next_due()
        self.assertIn('message', next_due)
        self.assertEqual(next_due['message'], 'All scheduled payments have been made')
    
    def test_get_current_payment_amount_non_active_loan(self):
        """Test that getting the current payment amount for a non-active loan raises an error."""
        loan = Loan(10000, 12, 5.0)
        # Loan is still in 'pending' status
        
        with self.assertRaises(ValueError):
            loan.get_current_payment_amount()
    
    def test_get_current_payment_amount(self):
        """Test getting the current payment amount."""
        loan = Loan(10000, 12, 5.0)
        loan.approve_loan()
        
        payment_amount = loan.get_current_payment_amount()
        
        # The payment amount should include interest
        monthly_rate = loan.interest_rate / 100 / 12
        expected_amount = loan.balance + (loan.balance * monthly_rate)
        
        self.assertEqual(payment_amount, expected_amount)
    
    def test_interest_only_payment(self):
        """Test making a payment that only covers interest."""
        loan = Loan(10000, 12, 12.0)  # Higher interest rate for clearer testing
        loan.approve_loan()
        
        # Calculate monthly interest
        monthly_rate = loan.interest_rate / 100 / 12
        interest_amount = loan.balance * monthly_rate
        
        # Make a payment that just covers the interest
        loan.make_repayment(date.today(), interest_amount)
        
        # Check that interest was paid but principal remains unchanged
        self.assertAlmostEqual(loan.interest_paid, interest_amount, places=2)
        self.assertEqual(loan.principal_paid, 0.0)
        self.assertEqual(loan.balance, 10000)  # Balance should not change
    
    def test_payment_less_than_interest(self):
        """Test making a payment that does not even cover interest."""
        loan = Loan(10000, 12, 12.0)  # Higher interest rate for clearer testing
        loan.approve_loan()
        
        # Calculate monthly interest
        monthly_rate = loan.interest_rate / 100 / 12
        interest_amount = loan.balance * monthly_rate
        
        # Make a payment less than the interest
        partial_amount = interest_amount / 2
        loan.make_repayment(date.today(), partial_amount)
        
        # Check that all payment went to interest and no principal was paid
        self.assertAlmostEqual(loan.interest_paid, partial_amount, places=2)
        self.assertEqual(loan.principal_paid, 0.0)
        self.assertEqual(loan.balance, 10000)  # Balance should not change

if __name__ == '__main__':
    unittest.main()