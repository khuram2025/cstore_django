from accounts.models import Business
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Customer, CustomerAccount
from .serializers import CustomerSerializer, TransactionSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status

class CustomerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_businesses = request.user.businesses.all()
        customers = Customer.objects.filter(businesses__in=user_businesses).distinct()
        serializer = CustomerSerializer(customers, many=True)
        serialized_data = serializer.data
        print("Serialized Data Customers:", serialized_data)
        return Response(serializer.data)

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

            customer.businesses.add(business)
            return Response({'message': 'Customer linked to business'}, status=status.HTTP_200_OK)
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
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
class AddTransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("Received request data for new transaction:", request.data)

        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            customer_account_id = serializer.validated_data.get('customer_account').id
            print(f"Validated customer account ID: {customer_account_id}")

            # Ensure the customer account is associated with one of the user's businesses
            customer_account = get_object_or_404(CustomerAccount, id=customer_account_id)
            user_businesses = request.user.businesses.all()

            if customer_account.business in user_businesses:
                # Save the transaction if the customer account's business is owned by the user
                saved_transaction = serializer.save()
                print(f"Transaction saved successfully with ID: {saved_transaction.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # If the business does not belong to the user, deny access
                print("Attempt to add transaction to a business not owned by the user.")
                return Response({'message': 'You do not have permission to add transactions for this customer account.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # If data is invalid, return an error response
            print("Received invalid data for transaction:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


        