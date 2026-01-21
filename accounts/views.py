from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
# from .models import Category, Product, Purchase
# from .models import Purchase, Stock



def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1']
        )
        return redirect('login')
    return render(request, 'auths/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("USERNAME:", username)
        print("PASSWORD:", password)
        user = authenticate(request, username=username, password=password)
        print("AUTH USER:", user)
        if user is not None:
            login(request, user)
            print("LOGIN SUCCESS")
            return redirect('dashboard')  
        else:
            error = "Invalid username or password"
            print("LOGIN FAILED")
            return render(request, 'auths/login.html', {'error': error})
    return render(request, 'auths/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    return render(request, 'auths/home.html')