import gradio as gr
from datetime import date, timedelta
from loans import Loan, get_current_date

# Global variable to store the current loan
current_loan = None

def apply_for_loan(amount, term, interest_rate):
    """Create a new loan application"""
    global current_loan
    try:
        amount = float(amount)
        term = int(term)
        interest_rate = float(interest_rate)
        
        if amount <= 0 or term <= 0 or interest_rate <= 0:
            return "Error: All values must be positive"
        
        current_loan = Loan(amount=amount, term=term, interest_rate=interest_rate)
        return f"Loan application created successfully! Loan ID: {current_loan.loan_id}, Status: {current_loan.status}"
    except ValueError as e:
        return f"Error: {str(e)}"

def approve_current_loan():
    """Approve the current loan"""
    global current_loan
    try:
        if current_loan is None:
            return "Error: No loan application exists"
        
        current_loan.approve_loan()
        return f"Loan approved successfully! Start date: {current_loan.start_date}, Status: {current_loan.status}"
    except ValueError as e:
        return f"Error: {str(e)}"

def make_payment(payment_amount):
    """Make a payment towards the current loan"""
    global current_loan
    try:
        if current_loan is None:
            return "Error: No loan application exists"
        
        payment_amount = float(payment_amount)
        if payment_amount <= 0:
            return "Error: Payment amount must be positive"
        
        payment_date = get_current_date()  # Use the current date for payment
        current_loan.make_repayment(payment_date, payment_amount)
        
        loan_state = current_loan.get_total_paid()
        return f"Payment of ${payment_amount:.2f} made successfully!\n" \
               f"Total paid: ${loan_state['total_paid']:.2f}\n" \
               f"Interest paid: ${loan_state['interest_paid']:.2f}\n" \
               f"Principal paid: ${loan_state['principal_paid']:.2f}\n" \
               f"Remaining balance: ${loan_state['remaining_balance']:.2f}\n" \
               f"Current status: {current_loan.status}"
    except ValueError as e:
        return f"Error: {str(e)}"

def get_loan_details():
    """Get details about the current loan"""
    global current_loan
    if current_loan is None:
        return "No loan application exists"
    
    details = f"Loan ID: {current_loan.loan_id}\n" \
              f"Amount: ${current_loan.amount:.2f}\n" \
              f"Term: {current_loan.term} months\n" \
              f"Interest Rate: {current_loan.interest_rate}%\n" \
              f"Status: {current_loan.status}\n"
    
    if current_loan.status != 'pending':
        details += f"Start Date: {current_loan.start_date}\n"
        loan_state = current_loan.get_total_paid()
        details += f"Total Paid: ${loan_state['total_paid']:.2f}\n" \
                   f"Interest Paid: ${loan_state['interest_paid']:.2f}\n" \
                   f"Principal Paid: ${loan_state['principal_paid']:.2f}\n" \
                   f"Remaining Balance: ${loan_state['remaining_balance']:.2f}\n"
        
        if current_loan.status == 'active':
            try:
                next_due = current_loan.get_next_due()
                details += f"\nNext Payment:\n" \
                           f"Due Date: {next_due['due_date']}\n" \
                           f"Payment Amount: ${next_due['payment_amount']:.2f}\n" \
                           f"Principal: ${next_due['principal']:.2f}\n" \
                           f"Interest: ${next_due['interest']:.2f}"
            except ValueError as e:
                details += f"\nCannot get next due information: {str(e)}"
    
    return details

def get_amortization_schedule():
    """Get the amortization schedule for the current loan"""
    global current_loan
    try:
        if current_loan is None:
            return "No loan application exists"
        
        if current_loan.status == 'pending':
            return "Cannot generate amortization schedule for a pending loan. Please approve the loan first."
        
        schedule = current_loan.generate_amortization_schedule()
        schedule_text = "Month | Date | Payment | Principal | Interest | Remaining Balance\n"
        schedule_text += "-" * 70 + "\n"
        
        for payment in schedule:
            schedule_text += f"{payment['month']:5d} | {payment['date']} | ${payment['payment']:.2f} | " \
                            f"${payment['principal']:.2f} | ${payment['interest']:.2f} | ${payment['remaining_balance']:.2f}\n"
        
        return schedule_text
    except ValueError as e:
        return f"Error: {str(e)}"

def clear_loan():
    """Clear the current loan (for demo purposes)"""
    global current_loan
    current_loan = None
    return "Current loan has been cleared. You can now create a new loan application."

# Create the Gradio interface
with gr.Blocks(title="Personal Banking Loan Management System") as app:
    gr.Markdown("# Personal Banking Loan Management System")
    
    with gr.Tab("Apply for Loan"):
        gr.Markdown("## Apply for a New Loan")
        with gr.Row():
            amount_input = gr.Number(label="Loan Amount ($)", value=10000)
            term_input = gr.Number(label="Term (months)", value=12)
            interest_rate_input = gr.Number(label="Annual Interest Rate (%)", value=5.0)
        apply_button = gr.Button("Apply for Loan")
        apply_output = gr.Textbox(label="Application Result")
        apply_button.click(apply_for_loan, inputs=[amount_input, term_input, interest_rate_input], outputs=apply_output)
    
    with gr.Tab("Loan Management"):
        gr.Markdown("## Manage Current Loan")
        with gr.Row():
            col1, col2 = gr.Column(scale=1), gr.Column(scale=1)
            
            with col1:
                approve_button = gr.Button("Approve Loan")
                approve_output = gr.Textbox(label="Approval Result")
                approve_button.click(approve_current_loan, inputs=[], outputs=approve_output)
                
                gr.Markdown("### Make a Payment")
                payment_amount = gr.Number(label="Payment Amount ($)", value=0)
                payment_button = gr.Button("Make Payment")
                payment_output = gr.Textbox(label="Payment Result")
                payment_button.click(make_payment, inputs=[payment_amount], outputs=payment_output)
                
                clear_button = gr.Button("Clear Current Loan (Demo)", variant="secondary")
                clear_output = gr.Textbox(label="Clear Result")
                clear_button.click(clear_loan, inputs=[], outputs=clear_output)
            
            with col2:
                details_button = gr.Button("Show Loan Details")
                loan_details = gr.Textbox(label="Loan Details", lines=12)
                details_button.click(get_loan_details, inputs=[], outputs=loan_details)
    
    with gr.Tab("Amortization Schedule"):
        gr.Markdown("## Loan Amortization Schedule")
        schedule_button = gr.Button("Generate Amortization Schedule")
        schedule_output = gr.Textbox(label="Amortization Schedule", lines=20)
        schedule_button.click(get_amortization_schedule, inputs=[], outputs=schedule_output)

# Launch the app
if __name__ == "__main__":
    app.launch()