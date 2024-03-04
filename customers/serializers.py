from accounts.models import Business
from rest_framework import serializers
from .models import Customer, CustomerAccount, Transaction

class CustomerSerializer(serializers.ModelSerializer):
    businesses = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=Business.objects.all())

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'businesses']



class CustomerAccountSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    mobile_number = serializers.CharField(source='customer.phone', read_only=True)
    
    class Meta:
        model = CustomerAccount
        fields = ['customer_name', 'mobile_number', 'opening_balance']



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['customer_account', 'date', 'time', 'amount', 'transaction_type', 'notes', 'attachment']
