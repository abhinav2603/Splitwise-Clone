from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
#from .models import User as myUser, Group as myGroup, Transaction, TransactionDetail, UpdatedpForm
#from .forms import RegisterForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

def redirect_dashboard(request):
    return redirect('dashboard:index')

def redirect_dash(request):
    return redirect('dashboard:index')