from accounts.models import Business
from rest_framework import serializers
from .models import Customer, CustomerAccount, Transaction
from django.db.models import Sum
from decimal import Decimal


class CustomerSerializer(serializers.ModelSerializer):
    businesses = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=Business.objects.all())

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'businesses']
    
    def get_total_balance(self, obj):
        total_balance = 0
        customer_accounts = CustomerAccount.objects.filter(customer=obj)
        for account in customer_accounts:
            opening_balance = account.opening_balance
            given_amount = account.transactions.filter(transaction_type='Given').aggregate(Sum('amount'))['amount__sum'] or 0
            taken_amount = account.transactions.filter(transaction_type='Take').aggregate(Sum('amount'))['amount__sum'] or 0
            account_balance = opening_balance + taken_amount - given_amount
            total_balance += account_balance
        return total_balance




class CustomerAccountSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    mobile_number = serializers.CharField(source='customer.phone', read_only=True)
    total_balance = serializers.SerializerMethodField()

    class Meta:
        model = CustomerAccount
        fields = ['id', 'customer_name', 'mobile_number', 'opening_balance', 'total_balance']

    def get_total_balance(self, obj):
        total_given = Transaction.objects.filter(customer_account=obj, transaction_type='Given').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_taken = Transaction.objects.filter(customer_account=obj, transaction_type='Take').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Ensure total_given and total_taken are Decimal
        total_given = Decimal(total_given)
        total_taken = Decimal(total_taken)

        total_balance = obj.opening_balance + total_given - total_taken
        return total_balance



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'customer_account', 'date', 'time', 'amount', 'transaction_type', 'notes', 'attachment']
