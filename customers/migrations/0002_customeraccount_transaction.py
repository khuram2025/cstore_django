# Generated by Django 3.2.16 on 2024-03-03 05:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_business_user'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opening_balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_accounts', to='accounts.business')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='customers.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('Take', 'Take'), ('Given', 'Given')], max_length=5)),
                ('notes', models.TextField(blank=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='attachments/')),
                ('customer_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='customers.customeraccount')),
            ],
        ),
    ]
