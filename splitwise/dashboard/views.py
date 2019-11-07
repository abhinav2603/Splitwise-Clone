from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages

# Create your views here.
def index(request):
	return HttpResponse("Dashboard");

def register(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		user = form.save()
		username = form.cleaned_data.get('username')
		login(request,user)
		messages.success(request, f"New account created: {username}")
		return redirect("dashboard:index")
	
	form = UserCreationForm
	return render(request = request,
			template_name = "dashboard/register.html",
			context={"form":form})

def logout_request(request):http://127.0.0.1:8000/dashboard/lgoin
	logout(request)
	messages.info(request, "Logged out successfully!")
	return redirect("dashboard:index")

def login_request(request):
	if request.method == 'POST':
		form = AuthenticationForm(request=request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}")
				return redirect('dashboard:index')
			else:
				messages.error(request, "Invalid username or password.")
		else:
			messages.error(request, "Invalid username or password.")
	form = AuthenticationForm()
	return render(request = request,
		template_name = "dashboard/login.html",
		context={"form":form})
