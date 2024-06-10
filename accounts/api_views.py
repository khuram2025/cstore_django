from django.contrib.auth import authenticate

from accounts.utils import send_otp_via_whatsapp
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer, LoginSerializer, SignupSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            password = serializer.validated_data['password']
            user = authenticate(request, mobile=mobile, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                # Assuming each user has one business, get the first one
                business = user.businesses.first()
                business_id = business.id if business else None
                return Response({
                    'token': token.key,
                    'business_name': user.business_name,
                    'business_id': business_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the user's auth token to log them out
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Signup successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Serialize the logged in user's data
        serializer = CustomUserSerializer(request.user)
        serialized_data = serializer.data
        print("Serialized Data:", serialized_data)
        return Response(serializer.data)
    


import logging
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OTP
from .serializers import RequestOTPSerializer, VerifyOTPSerializer
from .utils import send_otp_via_whatsapp

# Configure the logger
logger = logging.getLogger(__name__)

User = get_user_model()

class RequestOTPView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            try:
                user = User.objects.get(mobile=mobile)
                otp, created = OTP.objects.get_or_create(user=user)
                otp.save()
                sid = send_otp_via_whatsapp(mobile, otp.otp)
                if sid:
                    logger.info(f"OTP sent to {mobile} via WhatsApp, SID: {sid}")
                    return Response({'message': 'OTP sent'}, status=status.HTTP_200_OK)
                else:
                    logger.error(f"Failed to send OTP to {mobile} via WhatsApp")
                    return Response({'message': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except User.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(mobile=mobile)
                otp_record = OTP.objects.filter(user=user, otp=otp).first()
                if otp_record:
                    user.set_password(new_password)
                    user.save()
                    otp_record.delete()
                    return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
