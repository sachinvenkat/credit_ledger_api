from rest_framework import serializers
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        # We explicitly list the fields we want to expose to the outside world
        fields = [ 'id', 'name', 'balance', 'create_at']
        # We make 'balance' read-only so users can't arbitrarily change their balance via an API PUT request. 
        read_only_fields = ['balance']