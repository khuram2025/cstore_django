from django.db import models

from accounts.models import Business


class Customer(models.Model):
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15)
    businesses = models.ManyToManyField(Business, related_name='customers')

    def __str__(self):
        return self.name


class CustomerAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='accounts')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='customer_accounts')
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.customer.name} - {self.business.name}"


class Transaction(models.Model):
    TAKE = 'Take'
    GIVEN = 'Given'

    TRANSACTION_CHOICES = [
        (TAKE, 'Take'),
        (GIVEN, 'Given'),
    ]

    customer_account = models.ForeignKey(CustomerAccount, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    time = models.TimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=5, choices=TRANSACTION_CHOICES)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)

    def __str__(self):
        return f"{self.customer_account.customer.name} - {self.amount} - {self.transaction_type}"
