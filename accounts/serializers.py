from accounts.models import CustomUser
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response



class LoginSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    password = serializers.CharField(write_only=True)

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('mobile', 'password', 'name', 'business_name')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            mobile=validated_data['mobile'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            business_name=validated_data['business_name']
        )
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['mobile', 'name', 'business_name']


