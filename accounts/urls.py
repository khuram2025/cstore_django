from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    # other paths

    path('api/login/', api_views.LoginAPIView.as_view(), name='api_login'),

    path('api/request-otp/', api_views.RequestOTPView.as_view(), name='request_otp'),
    path('api/verify-otp/', api_views.VerifyOTPView.as_view(), name='verify_otp'),
    
    path('api/signup/', api_views.SignupAPIView.as_view(), name='api_signup'),

    path('api/home/', api_views.HomeView.as_view(), name='api_home'),
    path('api/logout/', api_views.LogoutAPIView.as_view(), name='logout'),


]

