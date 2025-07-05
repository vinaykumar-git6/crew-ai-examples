#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from engineering_team.crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

requirements = """
A simple loan management system for a personal banking platform.

The system should allow users to apply for a loan by specifying an amount, term (in months), and interest rate.
The system should store the loan as pending until it is approved by an administrator.
Once approved, the loan is marked as active and funds are considered disbursed.

The system should allow users to make monthly repayments toward the loan.
The system should calculate the remaining balance, interest paid, and principal paid so far.
The system should prevent users from overpaying (i.e., paying more than the remaining balance).

The system should be able to report:
  - The status of a loan (pending, active, paid)
  - The amortization schedule (month-by-month breakdown of principal and interest)
  - The total amount paid by the user and how much is left
  - The next due date and expected payment amount

The system should raise an error if a user tries to repay a loan that is not yet approved or already fully paid.

A function `get_current_date()` is provided to simulate the system's current date.

Includes a test implementation for:
  - A simple fixed interest rate loan
  - A user making partial and full payments

Minimize the number of test cases to just 3
"""
module_name = "loans.py"
class_name = "Loan"

def run():
    """
    Run the crew.
    """
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }
    
    try:
        EngineeringTeam().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


