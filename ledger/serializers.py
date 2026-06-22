from rest_framework import serializers
from .models import Account, Loan

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        # We explicitly list the fields we want to expose to the outside world
        fields = [ 'id', 'name', 'balance', 'create_at']
        # We make 'balance' read-only so users can't arbitrarily change their balance via an API PUT request. 
        read_only_fields = ['balance']

class LoanSearilizer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'principal_amount', 'interest_rate', 'status', 'created_at']
        # Critical Security Measure
        read_only_fileds = ['status']
