from django.shortcuts import render, redirect
from django.urls import reverse

from accounts.models import Business
from .forms import CustomUserCreationForm

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Check if a business name was provided
            business_name = form.cleaned_data.get('business_name')
            if business_name:
                # Create a new business instance
                Business.objects.create(name=business_name)

            return redirect(reverse('login'))
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            mobile = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(mobile=mobile, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to a home page or dashboard
            else:
                # Invalid login error handling
                pass
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
