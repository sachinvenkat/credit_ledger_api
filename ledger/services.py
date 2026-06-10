from decimal import Decimal
from django.db import transaction
from .models import Account, Transaction

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
