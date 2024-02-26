from accounts.models import Business
from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    businesses = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=Business.objects.all())

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'businesses']
