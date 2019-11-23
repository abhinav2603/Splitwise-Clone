from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import User as myUser, Group as myGroup, Transaction, TransactionDetail, NewGroupForm
from .forms import ProfileForm, TransactionForm, TransactionDetailForm
import logging
import datetime

# Create your views here.
def index(request):
	if request.user.is_authenticated:
		return redirect("dashboard:dashboard");
	else:
		return redirect("dashboard:login");

def register(request):
	form = UserCreationForm(request.POST or None)
	if request.method == "POST":
		#form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			login(request,user)
			messages.success(request, f"New account created: {username}")
			newUser=myUser(user_name=username)
			newUser.save()
			zeroGrp=myGroup.objects.get(group_id=0)
			zeroGrp.users.add(newUser)
			return redirect("dashboard:index")
	#form = UserCreationForm

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
	nonfriend=myUser.objects.exclude(friends__in=[user])
	formType=1
	participants_list=[]
	transaction=None
	transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
	if request.method=="POST":
		if formType==1:
			trForm=TransactionForm(request.POST, user_id=user_id)
			if trForm.is_valid():
				participants_list,transaction=handleTransaction(request)
				formType=2
				transactionForm=TransactionDetailForm(participants_list=participants_list)
			
		else:
			trForm=TransactionDetailForm(request.POST,participants_list=participants_list)
			if trForm.is_valid():
				handleTransactionDetail(request,participants_list,transaction)
				formType=1

	return render(request,'dashboard/pers_page.html',{'user':user,"nonfriend":nonfriend, "transForm":transactionForm});


def handleTransaction(request):
	user_id=request.user.id
	trForm=TransactionForm(request.POST, user_id=user_id)
	transaction=trForm.save()
	title=trForm.cleaned_data.get('title')
	trans_type=trForm.cleaned_data.get('trans_type')
	date=trForm.cleaned_data.get('date')
	group=trForm.cleaned_data.get('group')
	participants=trForm.cleaned_data.get('participants')
	newTransaction=Transaction(title=title,trans_type=trans_type,date=date,group=group)
	#newTransaction.save()
	participants_list=[]
	for user in participants:
		#newTransaction.participants.add(user)
		participants_list.append(user)
	#newTransaction.save()
	participants_list.append(myUser.objects.get(pk=user_id))
	return (participants_list,transaction)

def handleTransactionDetail(request,participants_list,transaction):
	user_id=request.user.id
	trForm=TransactionDetailForm(request.POST,participants_list=participants_list)
	if trForm.is_valid():
		gave_extra=[]
		gave_less=[]
		for participant in participants_list:
			given=trForm.cleaned_data.get(str(participant.id)+'gave')-trForm.cleaned_data.get(str(participant.id)+'share')
			if given>0:
				gave_extra.append[(participant,given)]
			else:
				gave_less.append[(participant,-given)]
		gave_extra.sort(key=lambda tup:tup[1],reverse=True)
		gave_less.sort(key=lambda tup:tup[1], reverse=True)

		while len(gave_extra)!=0:
			if gave_extra[0][1]>gave_less[0][1]:
				newTransactionDetail=TransactionDetail(trans=transaction,creditor=gave_extra[0][0],debitor=gave_less[0][0],lent=gave_less[0][1])
				newTransactionDetail.save()
				gave_extra[0][1]=gave_extra[0][1]=gave_less[0][1]
				del gave_less[0]
				gave_extra.sort(key=lambda tup:tup[1],reverse=True)
				gave_less.sort(key=lambda tup:tup[1], reverse=True)
			else:
				newTransactionDetail=TransactionDetail(trans=transaction,creditor=gave_extra[0][0],debitor=gave_less[0][0],lent=gave_extra[0][1])
				newTransactionDetail.save()
				gave_less[0][1]=gave_less[0][1]=gave_extra[0][1]
				del gave_extra[0]
				if gave_less[0][1]==0:
					del gave_less[0]
				gave_extra.sort(key=lambda tup:tup[1],reverse=True)
				gave_less.sort(key=lambda tup:tup[1], reverse=True)		



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
	transactions=group.transaction_set.all()
	return render(request,'dashboard/group_page.html',{
		'group':group,
		'user':user,
		'transactions':transactions,
		});

def my_group(request):
	user_id = request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	#logger = logging.getLogger(__name__)
	if request.method=="POST":
		form=NewGroupForm(request.POST,user_id=request.user.id)
		if form.is_valid():
			group_name=form.cleaned_data.get('group_name')
			participants=form.cleaned_data.get('users')
			group_id=myGroup.objects.all().count()
			#logger.error(group_name)
			newGrp=myGroup(group_name=group_name,group_id=group_id)
			newGrp.save()
			newGrp.users.add(user)
			for part in participants:
				newGrp.users.add(part)
			newGrp.save()
			return redirect("dashboard:all_groups")
	else:
		form=NewGroupForm(user_id=request.user.id)

	return render(request,'dashboard/pers_group.html',{'user':user,'form':form});

def addfriend(request,name):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	frnd=get_object_or_404(myUser, user_name=name)
	user.friends.add(frnd)
	return redirect('dashboard:dashboard');
	
