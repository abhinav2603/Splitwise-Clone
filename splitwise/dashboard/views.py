from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import User as myUser, Group as myGroup, Transaction, TransactionDetail

# Create your views here.
def index(request):
	if request.user.is_authenticated:
		return redirect("dashboard:dashboard");
	else:
		return redirect("dashboard:login");

def register(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		user = form.save()
		username = form.cleaned_data.get('username')
		login(request,user)
		messages.success(request, f"New account created: {username}")
		newUser=myUser(user_name=username)
		newUser.save()
		zeroGrp=myGroup.objects.get(group_id=0)
		zeroGrp.users.add(newUser)
		return redirect("dashboard:index")
	
	form = UserCreationForm
	return render(request = request,
			template_name = "dashboard/register.html",
			context={"form":form})

def logout_request(request):
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

def personal_page(request):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	return render(request,'dashboard/pers_page.html',{'user':user});

def friend_page(request,friend_id):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	friend=get_object_or_404(myUser, pk=friend_id)
	transactions=Transaction.objects.filter(participants__in=[user]).filter(participants__in=[friend])
	return render(request,'dashboard/friend_page.html',{
		'user':user,
		'friend':friend,
		'transactions':transactions})

def group_page(request,group_id):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	group = get_object_or_404(myGroup,group_id=group_id)
	return render(request,'dashboard/group_page.html',{
		'group':group,
		'user':user,
		});

def my_group(request):
	user_id = request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	return render(request,'dashboard/pers_group.html',{'user':user});
