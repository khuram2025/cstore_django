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


class CustomerCreateLinkView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        name = request.data.get('name')
        business_id = request.data.get('business_id')

        print(f"Received data - Phone: {phone}, Name: {name}, Business ID: {business_id}")  # Print received data

        # Check if customer already exists
        customer = Customer.objects.filter(phone=phone).first()
        if customer:
            print("Customer found, attempting to link to business")
            try:
                business = Business.objects.get(id=business_id)
            except Business.DoesNotExist:
                print(f"Business with ID {business_id} not found.")
                return Response({'message': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if CustomerAccount already exists for this customer and business
            customer_account, created = CustomerAccount.objects.get_or_create(customer=customer, business=business)
            if created:
                print("Created new CustomerAccount for existing customer and business.")
            else:
                print("CustomerAccount already exists for this customer and business.")

            customer.businesses.add(business)
            return Response({'message': 'Customer linked to business and CustomerAccount ensured'}, status=status.HTTP_200_OK)
        else:
            print("Customer not found, creating new customer")
            serializer = CustomerSerializer(data=request.data)
            if serializer.is_valid():
                customer = serializer.save()
                try:
                    business = Business.objects.get(id=business_id)
                except Business.DoesNotExist:
                    print(f"Business with ID {business_id} not found.")
                    return Response({'message': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)
                    
                customer.businesses.add(business)
                
                # Create CustomerAccount for the new customer and business
                CustomerAccount.objects.create(customer=customer, business=business)
                print("Created new CustomerAccount for new customer and business.")

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerAccountListView(generics.ListAPIView):
    serializer_class = CustomerAccountSerializer
    permission_classes = [IsAuthenticated]

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

        # Assuming total_sum as the sum of all 'Given' transactions minus all 'Take' transactions
        total_sum = total_sum_given - total_sum_taken

        # Adding the calculated data to the response
        response_data = {
            'total_customers': total_customers,
            'total_sum': total_sum,
            'accounts': data
        }
        
        print("Response Data:", response_data)
        
        return Response(response_data)
       
class AddTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Received request data:", request.data)  # Print the incoming request data

        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure the customer account belongs to the business of the logged-in user
            customer_account_id = serializer.validated_data['customer_account'].id
            customer_account = CustomerAccount.objects.filter(id=customer_account_id, business__user=request.user).first()
            
            if not customer_account:
                print("Customer account not found in user's business")  # Print error if the customer account is not found
                return Response({"error": "Customer account not found in your business"}, status=status.HTTP_404_NOT_FOUND)
            
            # Save the transaction since the customer account is valid
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