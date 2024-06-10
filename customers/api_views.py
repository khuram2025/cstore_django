from accounts.models import Business
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Customer, CustomerAccount, Transaction
from .serializers import CustomerAccountSerializer, CustomerSerializer, TransactionSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics
from django.db.models import Sum, Count
from decimal import Decimal

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics



class CustomerCreateLinkView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        name = request.data.get('name')
        business_id = request.data.get('business_id')

        print(f"Received data - Phone: {phone}, Name: {name}, Business ID: {business_id}")  # Print received data

        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            print(f"Business with ID {business_id} not found.")
            return Response({'message': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if customer already exists within the same business
        if Customer.objects.filter(phone=phone, businesses=business).exists():
            print("Customer already exists for this business.")
            return Response({'message': 'Customer already exists for this business'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if customer exists globally
        customer = Customer.objects.filter(phone=phone).first()
        if customer:
            print("Customer found, linking to business")
            customer.businesses.add(business)
            CustomerAccount.objects.get_or_create(customer=customer, business=business)
            return Response({'message': 'Customer linked to business and CustomerAccount ensured'}, status=status.HTTP_200_OK)
        else:
            print("Customer not found, creating new customer")
            serializer = CustomerSerializer(data=request.data)
            if serializer.is_valid():
                customer = serializer.save()
                customer.businesses.add(business)
                CustomerAccount.objects.create(customer=customer, business=business)
                print("Created new CustomerAccount for new customer and business.")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerAccountListView(generics.ListAPIView):
    serializer_class = CustomerAccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]  # Include DjangoFilterBackend if you plan on using other types of filtering alongside search.
    search_fields = ['customer__name', 'customer__phone']

    def get_queryset(self):
        user = self.request.user
        business = user.businesses.first()
        if not business:
            return CustomerAccount.objects.none()
        return CustomerAccount.objects.filter(business=business)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        
        # Calculate additional data
        total_customers = queryset.count()
        total_sum_given = Transaction.objects.filter(
            customer_account__in=queryset, 
            transaction_type=Transaction.GIVEN
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        total_sum_taken = Transaction.objects.filter(
            customer_account__in=queryset, 
            transaction_type=Transaction.TAKE
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Adding explicitly what the business will pay and receive
        total_sum_paid = total_sum_given
        total_sum_received = total_sum_taken

        # Assuming total_sum as the net balance (what will be received minus what will be paid)
        total_net_balance = total_sum_received - total_sum_paid

        # Adding the calculated data to the response
        response_data = {
            'total_customers': total_customers,
            'total_sum_paid': total_sum_paid,
            'total_sum_received': total_sum_received,
            'total_net_balance': total_net_balance,
            'accounts': data
        }
        
        return Response(response_data)
    
       
class AddTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Received request data:", request.data)  # Print the incoming request data

        customer_data = request.data.pop('customer_account')
        customer_info = customer_data['customer']
        business_id = customer_data['business']
        
        # Find the customer
        customer, created = Customer.objects.get_or_create(
            phone=customer_info['phone'],
            defaults={'name': customer_info['name']}
        )
        
        # Find the business
        business = Business.objects.get(id=business_id)

        # Find or create the customer account
        customer_account, created = CustomerAccount.objects.get_or_create(
            customer=customer,
            business=business,
            defaults={'opening_balance': 0.00}
        )

        # Add the customer account to the request data
        request.data['customer_account'] = customer_account.id

        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.save()
            print("Transaction saved successfully:", transaction.id)  # Print success message with transaction ID
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("Serializer errors:", serializer.errors)  # Print serializer errors if the data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerAccountEditProfileView(APIView):
    def put(self, request, account_id):
        try:
            customer_account = CustomerAccount.objects.get(id=account_id)
        except CustomerAccount.DoesNotExist:
            return Response({'message': 'CustomerAccount not found'}, status=status.HTTP_404_NOT_FOUND)

        # Extracting fields from request
        name = request.data.get('name')
        phone = request.data.get('phone')
        opening_balance = request.data.get('opening_balance')

        # Update the Customer model
        customer = customer_account.customer
        if name:
            customer.name = name
        if phone:
            customer.phone = phone
        customer.save()

        # Update the CustomerAccount model
        if opening_balance is not None:
            customer_account.opening_balance = opening_balance
        customer_account.save()

        # Prepare the response using serializers
        customer_data = CustomerSerializer(customer).data
        customer_account_data = CustomerAccountSerializer(customer_account).data
        # Combine customer and customer account data in the response
        response_data = {**customer_data, **customer_account_data}

        return Response(response_data, status=status.HTTP_200_OK)


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, customer_account_id):
        # Ensure the customer account belongs to the business of the logged-in user
        customer_account = get_object_or_404(CustomerAccount, id=customer_account_id, business__user=request.user)

        # Fetch transactions for the specified customer account
        transactions = Transaction.objects.filter(customer_account=customer_account)
        
        # Serialize and return the transactions
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, transaction_id, user):
        """
        Helper method to get the transaction object with user and transaction_id validation.
        """
        return get_object_or_404(Transaction, id=transaction_id, customer_account__business__user=user)

    def get(self, request, transaction_id):
        """
        Retrieve a single transaction.
        """
        transaction = self.get_object(transaction_id, request.user)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    def put(self, request, transaction_id):
        """
        Update a transaction.
        """
        transaction = self.get_object(transaction_id, request.user)
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, transaction_id):
        """
        Delete a transaction.
        """
        transaction = self.get_object(transaction_id, request.user)
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

