from django.test import TestCase
from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Account
from django.urls import reverse
# Create your tests here.
class LedgerAPITestCase(APITestCase):
    def setUp(self):
        # Create a test account with an initial balance
        # Arrange: This runs before EVERY single test. It sets up a fresh database state.
        self.account = Account.objects.create(name="Test Wallet", balance=Decimal('100.00'))
        #self.url = f'/api/accounts/{self.account.id}/transactions/'
        self.url = reverse('account-transaction', kwargs={'account_id': self.account.id})

    def test_successful_credit_updates_balance(self):
        # Act & Assert: Tests if a valid deposit actually saves to the database.
        payload = {"amount": "50.00", "transaction_type": "CREDIT"}
        
        # Simulate a POST request
        response = self.client.post(self.url, payload, format='json')
        
        # 1. Assert the HTTP response is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Refresh the account from the database to get the newly updated balance
        self.account.refresh_from_db()
        
        # 3. Assert the math is absolutely correct
        self.assertEqual(self.account.balance, Decimal('150.00'))

    def test_insufficient_funds_returns_400(self):
        """
        Act & Assert: Tests our fail-safe logic for overdrafts.
        """
        payload = {"amount": "999.00", "transaction_type": "DEBIT"}
        response = self.client.post(self.url, payload, format='json')
        
        # 1. Assert the API blocks the request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 2. Assert the database balance was NOT altered
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('100.00'))