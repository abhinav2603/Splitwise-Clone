from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import TransactionForm, TransactionDetailForm, TransactionParticipantsForm, RegisterForm


from .models import User as myUser, Group as myGroup, Transaction, TransactionDetail, NewGroupForm, UpdatedpForm, UploadFileForm

import logging
import datetime
import pdb

LOG_FILENAME = 'views.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

transFormType=1
participants_list=[]
title="the transaction"
trans_type="Others"
date=None
group=None
transaction=None

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
	if request.user.is_authenticated:
		return redirect("dashboard:dashboard");
	else:
		return redirect("dashboard:login");

def register(request):
	form = RegisterForm(request.POST or None)
	if request.method == "POST":
		#form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('first_name')
			email = form.cleaned_data.get('email')
			login(request,user)
			messages.success(request, f"New account created: {username}")
			newUser=myUser(user_name=username,email=email)
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
	#import pdb; pdb.set_trace()
	global transFormType
	global participants_list
	global title
	global trans_type
	global date
	global group
	global transaction
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	nonfriend=myUser.objects.exclude(friends__in=[user])
	#formType=1
	#participants_list=[]
	#title="the transaction"
	#trans_type="Others"
	#date=None
	#group=None
	#transaction=None
	transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
	if request.method=="POST":
		logging.debug('post request')
		if transFormType==1:
			logging.debug('formType=1')
			trForm=TransactionForm(request.POST, user_id=user_id)
			if trForm.is_valid():
				title,trans_type,date,group=handleTransaction(request,trForm)
				transFormType=2
				logging.debug('first form submitted')
				transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
			else:
				transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
			
		elif transFormType==2:
			logging.debug('formType=2')
			trForm=TransactionParticipantsForm(request.POST,user_id=request.user.id,group_id=group.group_id)
			logging.debug('submitted the second form')
			#breakpoint()
			#import pdb; pdb.set_trace()
			if trForm.is_valid():
				logging.debug('second form valid')
				participants_list=handleTransactionParticipants(request,trForm)
				transFormType=3
				logging.debug('Here')
				transactionForm=TransactionDetailForm(participants_list=participants_list)
			else:
				transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
		else:
			logging.debug('formType=3')
			trForm=TransactionDetailForm(request.POST,participants_list=participants_list)
			if trForm.is_valid():
				handleTransactionDetail(request,trForm,title,trans_type,date,group,participants_list)
				transFormType=1
				transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
			else:
				transactionForm=TransactionDetailForm(participants_list=participants_list)

	return render(request,'dashboard/pers_page.html',{'user':user,"nonfriend":nonfriend, "transForm":transactionForm,"trType":transFormType});


def handleTransaction(request,trForm):
	user_id=request.user.id
	#trForm=TransactionForm(request.POST, user_id=user_id)
	#transaction=trForm.save()
	newTransaction=None
	if trForm.is_valid():
		title=trForm.cleaned_data.get('title')
		trans_type=trForm.cleaned_data.get('trans_type')
		date=trForm.cleaned_data.get('date')
		group=trForm.cleaned_data.get('group')
	return (title,trans_type,date,group)

def handleTransactionParticipants(request,trForm):
	#trForm=TransactionParticipantsForm(request.POST,user=myUser.objects.get(request.user.id),group=group)
	participants_list=[]
	if trForm.is_valid():
		part=trForm.cleaned_data.get('participants')
		for participant in part:
			participants_list.append(participant)
		participants_list.append(myUser.objects.get(pk=request.user.id))
	return participants_list

def handleTransactionDetail(request,trForm,title,trans_type,date,group,participants_list):
	user_id=request.user.id
	newTransaction=Transaction(title=title,trans_type=trans_type,date=date,group=group)
	newTransaction.save()
	for participant in participants_list:
		newTransaction.participants.add(participant)
	newTransaction.save()
	#breakpoint()
	#trForm=TransactionDetailForm(request.POST,participants_list=participants_list)
	if trForm.is_valid():
		gave_extra=[]
		gave_less=[]
		for participant in participants_list:
			given=trForm.cleaned_data.get(str(participant.id)+'gave')-trForm.cleaned_data.get(str(participant.id)+'share')
			if given>0:
				gave_extra.append([participant,given])
			else:
				gave_less.append([participant,-given])
		gave_extra.sort(key=lambda tup:tup[1],reverse=True)
		gave_less.sort(key=lambda tup:tup[1], reverse=True)

		while len(gave_extra)!=0:
			if gave_extra[0][1]>gave_less[0][1]:
				newTransactionDetail=TransactionDetail(trans=newTransaction,creditor=gave_extra[0][0],debitor=gave_less[0][0],lent=gave_less[0][1])
				newTransactionDetail.save()
				gave_extra[0][1]=gave_extra[0][1]-gave_less[0][1]
				del gave_less[0]
				gave_extra.sort(key=lambda tup:tup[1],reverse=True)
				gave_less.sort(key=lambda tup:tup[1], reverse=True)
			else:
				newTransactionDetail=TransactionDetail(trans=newTransaction,creditor=gave_extra[0][0],debitor=gave_less[0][0],lent=gave_extra[0][1])
				newTransactionDetail.save()
				gave_less[0][1]=gave_less[0][1]-gave_extra[0][1]
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
	global transFormType
	global participants_list
	global title
	global trans_type
	global date
	global group
	global transaction
	transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
	if request.method=="POST":
		logging.debug('post request')
		if transFormType==1:
			logging.debug('formType=1')
			trForm=TransactionForm(request.POST, user_id=user_id)
			if trForm.is_valid():
				title,trans_type,date,group=handleTransaction(request,trForm)
				transFormType=2
				logging.debug('first form submitted')
				transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
			else:
				transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
			
		elif transFormType==2:
			logging.debug('formType=2')
			trForm=TransactionParticipantsForm(request.POST,user_id=request.user.id,group_id=group.group_id)
			logging.debug('submitted the second form')
			#breakpoint()
			#import pdb; pdb.set_trace()
			if trForm.is_valid():
				logging.debug('second form valid')
				participants_list=handleTransactionParticipants(request,trForm)
				transFormType=3
				logging.debug('Here')
				transactionForm=TransactionDetailForm(participants_list=participants_list)
			else:
				transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
		else:
			logging.debug('formType=3')
			trForm=TransactionDetailForm(request.POST,participants_list=participants_list)
			if trForm.is_valid():
				handleTransactionDetail(request,trForm,title,trans_type,date,group,participants_list)
				transFormType=1
				transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
			else:
				transactionForm=TransactionDetailForm(participants_list=participants_list)
	return render(request,'dashboard/friend_page.html',{
		'user':user,
		'friend':friend,
		'transactions':transactions, "transForm":transactionForm,"trType":transFormType})

def group_page(request,group_id):
	global transFormType
	global participants_list
	global title
	global trans_type
	global date
	global group
	global transaction
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	group = get_object_or_404(myGroup,group_id=group_id)
	transactions=group.transaction_set.all()
	transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
	if request.method=="POST":
		logging.debug('post request')
		if transFormType==1:
			logging.debug('formType=1')
			trForm=TransactionForm(request.POST, user_id=user_id)
			if trForm.is_valid():
				title,trans_type,date,group=handleTransaction(request,trForm)
				transFormType=2
				logging.debug('first form submitted')
				transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
			else:
				transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
			
		elif transFormType==2:
			logging.debug('formType=2')
			trForm=TransactionParticipantsForm(request.POST,user_id=request.user.id,group_id=group.group_id)
			logging.debug('submitted the second form')
			#breakpoint()
			#import pdb; pdb.set_trace()
			if trForm.is_valid():
				logging.debug('second form valid')
				participants_list=handleTransactionParticipants(request,trForm)
				transFormType=3
				logging.debug('Here')
				transactionForm=TransactionDetailForm(participants_list=participants_list)
			else:
				transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
		else:
			logging.debug('formType=3')
			trForm=TransactionDetailForm(request.POST,participants_list=participants_list)
			if trForm.is_valid():
				handleTransactionDetail(request,trForm,title,trans_type,date,group,participants_list)
				transFormType=1
				transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
			else:
				transactionForm=TransactionDetailForm(participants_list=participants_list)

	return render(request,'dashboard/group_page.html',{'user':user,"group":group, "transForm":transactionForm,"trType":transFormType, 'transactions':transactions});

def my_group(request):
	global transFormType
	global participants_list
	global title
	global trans_type
	global date
	global group
	global transaction
	user_id = request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	#logger = logging.getLogger(__name__)
	transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
	form=NewGroupForm(user_id=request.user.id)
	if request.method=="POST":
		logging.debug('post request')
		if 'submit' in request.POST:
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
		else:
			if transFormType==1:
				logging.debug('formType=1')
				trForm=TransactionForm(request.POST, user_id=user_id)
				if trForm.is_valid():
					title,trans_type,date,group=handleTransaction(request,trForm)
					transFormType=2
					logging.debug('first form submitted')
					transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
				else:
					transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
				
			elif transFormType==2:
				logging.debug('formType=2')
				trForm=TransactionParticipantsForm(request.POST,user_id=request.user.id,group_id=group.group_id)
				logging.debug('submitted the second form')
				#breakpoint()
				#import pdb; pdb.set_trace()
				if trForm.is_valid():
					logging.debug('second form valid')
					participants_list=handleTransactionParticipants(request,trForm)
					transFormType=3
					logging.debug('Here')
					transactionForm=TransactionDetailForm(participants_list=participants_list)
				else:
					transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
			else:
				logging.debug('formType=3')
				trForm=TransactionDetailForm(request.POST,participants_list=participants_list)
				if trForm.is_valid():
					handleTransactionDetail(request,trForm,title,trans_type,date,group,participants_list)
					transFormType=1
					transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
				else:
					transactionForm=TransactionDetailForm(participants_list=participants_list)

	return render(request,'dashboard/pers_group.html',{'user':user,"group":group, "transForm":transactionForm,"trType":transFormType,'form':form});

def addfriend(request,name):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	frnd=get_object_or_404(myUser, user_name=name)
	user.friends.add(frnd)
	return redirect('dashboard:dashboard')

def userprofile(request):
	user_id = request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	global transFormType
	global participants_list
	global title
	global trans_type
	global date
	global group
	global transaction
	transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
	if request.method=="POST":
		logging.debug('post request')
		if transFormType==1:
			logging.debug('formType=1')
			trForm=TransactionForm(request.POST, user_id=user_id)
			if trForm.is_valid():
				title,trans_type,date,group=handleTransaction(request,trForm)
				transFormType=2
				logging.debug('first form submitted')
				transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
			else:
				transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
			
		elif transFormType==2:
			logging.debug('formType=2')
			trForm=TransactionParticipantsForm(request.POST,user_id=request.user.id,group_id=group.group_id)
			logging.debug('submitted the second form')
			#breakpoint()
			#import pdb; pdb.set_trace()
			if trForm.is_valid():
				logging.debug('second form valid')
				participants_list=handleTransactionParticipants(request,trForm)
				transFormType=3
				logging.debug('Here')
				transactionForm=TransactionDetailForm(participants_list=participants_list)
			else:
				transactionForm=TransactionParticipantsForm(user_id=request.user.id,group_id=group.group_id)
		else:
			logging.debug('formType=3')
			trForm=TransactionDetailForm(request.POST,participants_list=participants_list)
			if trForm.is_valid():
				handleTransactionDetail(request,trForm,title,trans_type,date,group,participants_list)
				transFormType=1
				transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
			else:
				transactionForm=TransactionDetailForm(participants_list=participants_list)
	return render(request,'dashboard/profile.html',{'user':user, "transForm":transactionForm,"trType":transFormType})


def update_pic(request):
	user_id = request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	if request.method=="POST":
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			#form.save()
			user.dp=request.FILES['file']
			#user.dp=form.cleaned_data.get('dp')
			user.save()
			#a=form.cleaned_data.get('user_name')
			a=request.FILES['file']
			messages.info(request, f"You are in as {a}")
			return redirect('dashboard:index')
	else:
		form=UpdatedpForm()
	return render(request,'dashboard/changeMydp.html',{'user':user,'form':form});

@login_required(login_url='dashboard/dashboard')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard:login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'dashboard/change_password.html', {
        'form': form
    })

	
