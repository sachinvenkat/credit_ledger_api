from decimal import Decimal
from django.db import transaction
from .models import Account, Transaction, Loan

def  process_ledger_entry(account_id, amount:Decimal, transaction_type: str):
    # 1. atomic() ensures all-or-nothing execution
    with transaction.atomic():

        # 2. select_for_update() locks the database row
        account = Account.objects.select_for_update().get(id=account_id)

        if transaction_type == "DEBIT" and account.balance < amount:
            raise ValueError("Insufficient Funds. Transaction declined.")

        # update the balance in memory
        if transaction_type == "CREDIT":
            account.balance += amount
        elif transaction_type == "DEBIT":
            account.balance -= amount

        # Save the new balance to the database
        account.save()

        # Create the immutable transaction record
        txn = Transaction.objects.create(
            account = account,
            amount = amount,
            transaction_type = transaction_type,
        )

        return txn
    

def approve_and_disburse_loan(loan_id):
    with transaction.atomic():

        loan = Loan.objects.select_for_update().get(id=loan_id)

        if loan.status != 'PENDING':
            raise ValueError(f"Loan cannot be disbursed. Current loan status is {loan.status}.")
        
        loan.status = 'ACTIVE'
        loan.save() 

        process_ledger_entry(
            account_id=loan.account.id,
            amount = loan.principal_amount,
            transaction_type='CREDIT'
        )
        return loan
    
def process_loan_repayment(loan_id, payment_amount: Decimal):
    with transaction.atomic():
        loan = Loan.objects.select_for_update().get(id=loan_id)

        if loan.status != 'ACTIVE':
            raise ValueError(f"Cannot repay loan with status: {loan.status}")
    
        if payment_amount <= 0:
            raise ValueError("Repayment amount must ve strictly positive.")
        
        if payment_amount > loan.outstanding_balance:
            raise ValueError("Repayment amount cannot exceed the outstanding balance.")
        
        process_ledger_entry(
            account_id = loan.account.id,
            amount =  payment_amount,
            transaction_type="DEBIT"
        )

        loan.outstanding_balance -= payment_amount 

        if loan.outstanding_balance == Decimal('0.00'):
            loan.status =  'REPAID'

        loan.save()

        return loan