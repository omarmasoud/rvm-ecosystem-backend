from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib import messages

# Import models if needed for context in web views (e.g., for login/signup success messages)
from .models import User


def home(request):
    """Root view: display login or redirect to admin if logged in"""
    if request.user.is_authenticated:
        return redirect('/admin/')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/admin/')  # Redirect to admin or a user dashboard
        else:
            return render(request, 'login.html', {'form': form})
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def user_signup(request):
    """Handle user registration via a template form"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'You have successfully signed up! This is the admin panel, where general user functionalities are not available.')
            return redirect('core:signup_success')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def signup_success_view(request):
    """Display success message after signup and inform user about admin panel."""
    return render(request, 'signup_success.html') 