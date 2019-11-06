from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login

# Create your views here.
def index(request):
	return HttpResponse("Dashboard");

def register(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		user = form.save()
		username = form.cleaned_data.get('username')
		login(request,user)
		return redirect("dashboard:index")
	
	form = UserCreationForm
	return render(request = request,
			template_name = "dashboard/login.html",
			context={"form":form})