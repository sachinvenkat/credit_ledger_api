from django.db import models
import uuid
from decimal import Decimal
# Create your models here.

class Account(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique secure identifier. Uses random UUID4 to prevent guessing account URLs.",
    )
    name =  models.CharField(
        max_length = 100,
        help_text="The legal or display name of the account holder (e.g., 'Sachin Venkatesh').",
    )

    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Current available funds. Decimal type is strictly used to eliminate floating-point rounding errors.",
    )
    # Audit Trails: auto_now_add records exactly when the ropyw was created. auto_now updates every time the row changes
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.balance}"
    

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('CREDIT', 'Credit'), # Money added from account
        ('DEBIT', 'Debit'),   # Money removed from account
    )
    id =  models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    # 1. The relational link
    account = models.ForeignKey(
        Account, 
        on_delete= models.PROTECT, 
        related_name = 'transactions'
    ) 

    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    # 2. Immutable timestamp
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of  ${self.amount} on {self.account.name}"
    
