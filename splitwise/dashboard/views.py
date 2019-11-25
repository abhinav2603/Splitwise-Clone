from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q

from .forms import TransactionForm, TransactionDetailForm, TransactionParticipantsForm, RegisterForm, ModifyTransactionForm, GroupSettleForm


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
from datetime import date

today = date.today()

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

#############################################################################################3

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
	transactions=Transaction.objects.filter(participants__in=[user])
	friend=user.friends.all()
	d=dict()
	for friend in friend:
		d[friend]=0
	for transaction in transactions:
		for transdet in transaction.transactiondetail_set.all():
			messages.info(request,f"{transdet.lent} {transdet.creditor}")
			credit=transdet.creditor
			debit=transdet.debitor
			lent=transdet.lent
			if credit == user:
				if debit in d.keys():
					d[debit]=d[debit]+lent
				else:
					d[debit]=lent
			elif debit == user:
				if credit in d.keys():
					d[credit]=d[credit]-lent
				else :
					d[credit]=(-1*lent)
	dtuple=dict()
	for k,v in d.items():
		dtuple[k]=(v,-v)
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
				logging.debug('this is valid')
				handleTransactionDetail(request,trForm,title,trans_type,date,group,participants_list)
				transFormType=1
				transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
			else:
				logging.debug('this is invalid')
				transactionForm=TransactionDetailForm(participants_list=participants_list)

	return render(request,'dashboard/personal_page.html',{'user':user,"nonfriend":nonfriend, "transForm":transactionForm,"trType":transFormType,'mydict':dtuple});

###############################################################################

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
		#participants_list.append(myUser.objects.get(pk=request.user.id))
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

		if group.group_id!=0:

			#now minimise transactions in the group
			gave_extra=[]
			gave_less=[]

			#the transaction object which minimises transactions
			transMinimiser=Transaction.objects.get(group=group,trans_type="mintrans")

			givDict={}

			for user in group.users.all():
				givDict[user]=0

			for transMinDet in transMinimiser.transactiondetail_set.all():
				givDict[transMinDet.creditor]+=transMinDet.lent
				givDict[transMinDet.debitor]-=transMinDet.lent

			for newTransDet in newTransaction.transactiondetail_set.all():
				givDict[newTransDet.creditor]+=newTransDet.lent
				givDict[newTransDet.debitor]-=newTransDet.lent

			for user in givDict.keys():
				if givDict[user]>0:
					gave_extra.append([user,givDict[user]])
				elif givDict[user]<0:
					gave_less.append([user,-givDict[user]])

			#now delete the existing transaction minimiser transactions
			TransactionDetail.objects.filter(trans=transMinimiser).delete()

			gave_extra.sort(key=lambda tup:tup[1],reverse=True)
			gave_less.sort(key=lambda tup:tup[1], reverse=True)

			logging.debug('gave_extra array is:')
			for i in gave_extra:
				logging.debug(i[0].user_name+' '+str(i[1]))

			logging.debug('gave_less array is:')
			for i in gave_less:
				logging.debug(i[0].user_name+' '+str(i[1]))

			while len(gave_extra)!=0:
				if gave_extra[0][1]>gave_less[0][1]:
					newTransactionDetail=TransactionDetail(trans=transMinimiser,creditor=gave_extra[0][0],debitor=gave_less[0][0],lent=gave_less[0][1])
					newTransactionDetail.save()
					gave_extra[0][1]=gave_extra[0][1]-gave_less[0][1]
					del gave_less[0]
					gave_extra.sort(key=lambda tup:tup[1],reverse=True)
					gave_less.sort(key=lambda tup:tup[1], reverse=True)
				else:
					newTransactionDetail=TransactionDetail(trans=transMinimiser,creditor=gave_extra[0][0],debitor=gave_less[0][0],lent=gave_extra[0][1])
					newTransactionDetail.save()
					gave_less[0][1]=gave_less[0][1]-gave_extra[0][1]
					del gave_extra[0]
					if gave_less[0][1]==0:
						del gave_less[0]
					gave_extra.sort(key=lambda tup:tup[1],reverse=True)
					gave_less.sort(key=lambda tup:tup[1], reverse=True)



##################################################################################

def friend_page(request,friend_id):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	friend=get_object_or_404(myUser, pk=friend_id)
	transactions=Transaction.objects.filter(participants__in=[user]).filter(participants__in=[friend])
	groups=myGroup.objects.filter(users__in=[user]).filter(users__in=[friend])
	d=dict()
	dtuple=dict()
	state='settled'
	for group1 in groups:
		d[group1]=0

	for group1 in groups:
		for transactions in group1.transaction_set.all():
			for transdet in transactions.transactiondetail_set.all():
				credit=transdet.creditor
				debit=transdet.debitor
				lent=transdet.lent
				if credit == user:
					d[group1]=d[group1]+lent
				elif debit==user:
					d[group1]=d[group1]-lent
	for k,v in d.items():
		if v != 0:
			state='unsettled'
			break
	for k,v in d.items():
		dtuple[k]=(v,-v)

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
	return render(request,'dashboard/friend_page.html',{'user':user,
		'friend':friend,
		'transactions':transactions, 
		"transForm":transactionForm,
		"trType":transFormType,
		'mydict':dtuple,
		'state':state})

###################################################################################3

def settleUp(request,friend_id):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	friend=get_object_or_404(myUser, pk=friend_id)
	transactions=Transaction.objects.filter(participants__in=[user]).filter(participants__in=[friend])
	groups=myGroup.objects.filter(users__in=[user]).filter(users__in=[friend])
	d=dict()
	for group in groups:
		d[group]=0
	for group in groups:
		for transactions in group.transaction_set.all():
			for transdet in transactions.transactiondetail_set.all():
				credit=transdet.creditor
				debit=transdet.debitor
				lent=transdet.lent
				if credit == user & debitor == friend:
					d[group]=d[group]+lent
				elif debit==user & creditor == friend:
					d[group]=d[group]-lent

	for k,v in d.items():
		if v > 0:
			newtrans=Transaction(group=k,title='Settled Up',trans_type='SettleUp',date=today)
			newtrans.save()
			newtrans.participants.add(user)
			newtrans.participants.add(friend)
			newtrans.save()
			newtransdet=TransactionDetail(trans=newtrans,creditor=friend,debitor=user,lent=v)
			newtransdet.save()
		elif v < 0:
			newtrans=Transaction(group=k,title='Settled Up',trans_type='SettleUp',date=today)
			newtrans.save()
			newtrans.participants.add(user)
			newtrans.participants.add(friend)
			newtrans.save()
			newtransdet=TransactionDetail(trans=newtrans,creditor=user,debitor=friend,lent=(-1*v))
			newtransdet.save()
	
	state='settled'
	return render(request,'dashboard/friend_page.html',{
		'user':user,
		'friend':friend,
		'transactions':transactions,
		'mydict':d,
		'state':state})

################################################################################

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
	settleForm=GroupSettleForm(group_id=group_id,user_id=user_id)
	if request.method=="POST":
		logging.debug('post request')
		if 'submit' in request.POST:
			settleForm=GroupSettleForm(request.POST,group_id=group_id,user_id=user_id)
			if settleForm.is_valid():
				settleUsers=settleForm.cleaned_data.get('users')
			else:
				settleForm=GroupSettleForm(group_id=group_id,user_id=user_id)
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

	dtuple=dict()
	for transactions in group.transaction_set.all():
		for transdet in transactions.transactiondetail_set.all():
			credit=transdet.creditor
			debit=transdet.debitor
			lent=transdet.lent
			messages.info(request,f'{credit}')
			messages.info(request,f'{debit}')
			messages.info(request,f'{lent}')
			dtuple[transdet]=(lent,-lent,credit,debit)

	return render(request,'dashboard/group_page.html',{'user':user,"group":group, "transForm":transactionForm,"trType":transFormType,'mydict':dtuple,'groupSettleForm':settleForm})

##########################################################################################

def my_group(request):
	user_id = request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	global transFormType
	global participants_list
	global title
	global trans_type
	global date
	global group
	global transaction
	#logger = logging.getLogger(__name__)
	transactionForm=TransactionForm(initial={'transType':'Others','date':datetime.date.today()},user_id=user_id)
	form=NewGroupForm(user_id=request.user.id)
	if request.method=="POST":
		logging.debug('post request')
		if 'submit' not in request.POST:
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

				#the transaction minimiser transaction
				newTransaction=Transaction(title="Min_trans",trans_type="mintrans",date=datetime.date.today(),group=newGrp)
				newTransaction.save()

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

	group1=myGroup.objects.filter(users__in=[user])
	d=dict()
	for group in group1:
		d[group]=0
	for group in group1:
		for transactions in group.transaction_set.all():
			for transdet in transactions.transactiondetail_set.all():
				credit=transdet.creditor
				debit=transdet.debitor
				lent=transdet.lent
				if credit == user:
					d[group]=d[group]+lent
				elif debit==user:
					d[group]=d[group]-lent
	dtuple=dict()
	for k,v in d.items():
		dtuple[k]=(v,-v)
	return render(request,'dashboard/pers_group.html',{'user':user,"group":group, "transForm":transactionForm,"trType":transFormType,'mydict':dtuple,"form":form});

def addfriend(request,name):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	frnd=get_object_or_404(myUser, user_name=name)
	user.friends.add(frnd)
	return redirect('dashboard:dashboard')

################################--------USER PRofile###########################################3
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

##################################3--------------LEAVE GROUP--------------------------##########################

def leave(request,group_id):
	user_id = request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	group2=get_object_or_404(myGroup,group_id=group_id)
	messages.info(request,group2.group_id)
	messages.info(request,group_id)
	sum=0
	for trans in group2.transaction_set.all():
		messages.info(request,trans)
		for transdet in trans.transactiondetail_set.all():
			if user == transdet.creditor:
				sum=sum+transdet.lent
			elif user == transdet.debitor:
				sum=sum-transdet.lent
	if sum == 0:
		group2.users.remove(user)
		group2.save()
	else:
		messages.error(request, group_id)
	global transFormType
	global participants_list
	global title
	global trans_type
	global date
	global group
	global transaction
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

	group1=myGroup.objects.filter(users__in=[user])
	d=dict()
	for group in group1:
		d[group]=0
	for group in group1:
		for transactions in group.transaction_set.all():
			for transdet in transactions.transactiondetail_set.all():
				credit=transdet.creditor
				debit=transdet.debitor
				lent=transdet.lent
				if credit == user:
					d[group]=d[group]+lent
				elif debit==user:
					d[group]=d[group]-lent
	dtuple=dict()
	for k,v in d.items():
		dtuple[k]=(v,-v)
	return render(request,'dashboard/pers_group.html',{'user':user,"group":group, "transForm":transactionForm,"trType":transFormType,'mydict':dtuple,"form":form});

############################-----------DELETE GROUP---------########################################3

def delete(request,group_id):
	state='settled'
	user_id=request.user.id
	user=get_object_or_404(myUser,pk=user_id)
	group2=get_object_or_404(myGroup,group_id=group_id)
	s=dict()
	for user in group2.users.all():
		s[user]=0
	for transactions in group2.transaction_set.all():
		for trans in transactions.transactiondetail_set.all():
			s[trans.creditor]=s[trans.creditor]+trans.lent
			s[trans.debitor]=s[trans.debitor]-trans.lent
	for k,v in s.items():
		if v != 0:
			state='unsettled'
			break
	if state == 'unsettled':
		messages.error(request,f'Not everyone is settled in the group!!')
	else:
		grp=myGroup.objects.get(group_id=group_id)
		grp.delete()

	group1=myGroup.objects.filter(users__in=[user])
	d=dict()
	for group in group1:
		d[group]=0
	for group in group1:
		for transactions in group.transaction_set.all():
			for transdet in transactions.transactiondetail_set.all():
				credit=transdet.creditor
				debit=transdet.debitor
				lent=transdet.lent
				if credit == user:
					d[group]=d[group]+lent
				elif debit==user:
					d[group]=d[group]-lent
	dtuple=dict()
	for k,v in d.items():
		dtuple[k]=(v,-v)
	return render(request,'dashboard/pers_group.html',{'user':user,"group":group,'mydict':dtuple});

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

def balance(request,group_id):
	user_id=request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	group2=get_object_or_404(myGroup,group_id=group_id)
	d1=dict()
	d2=dict()
	dtuple1=dict()
	dtuple2=dict()
	#for friend in group.users.filter(friend__in=[user]):
	#for participants in group.user_set.all():
	#	if 

	for transactions in group2.transaction_set.all():
		for transdet in transactions.transactiondetail_set.all():
			credit=transdet.creditor
			debit=transdet.debitor
			lent=transdet.lent
			if credit == user:
				if debit in d1.keys():
					d1[debit]=d1[debit]+lent
				else:
					d1[debit]=lent
			elif debit == user:
				if credit in d1.keys():
					d1[credit]=d1[credit]-lent
				else :
					d1[credit]=(-1*lent)

	for k,v in d1.items():
		dtuple1[k]=(v,-v)
	
	for transactions in group2.transaction_set.all():
		for transdet in transactions.transactiondetail_set.all():
			credit=transdet.creditor
			debit=transdet.debitor
			lent=transdet.lent
			if debit in d2.keys():
				d2[debit]=d2[debit]-lent
			else:
				d2[debit]=-lent
			if credit in d2.keys():
				d2[credit]=d2[credit]+lent
			else:
				d2[credit]=lent
	
	for k,v in d2.items():
		dtuple2[k]=(v,-v)

	return render(request,'dashboard/balance.html',{'user':user,"group":group2,'mydict1':dtuple1,'mydict2':dtuple2})

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

	
def activity(request):
	user_id=request.user.id
	user=myUser.objects.get(pk=user_id)
	transactions=Transaction.objects.filter(participants__in=[user]).order_by('-date')
	modifyForm=ModifyTransactionForm()
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
		if 'submit' in request.POST:
			logging.debug('post request for modify')
			modifyForm=ModifyTransactionForm(request.POST)
			if modifyForm.is_valid():
				logging.debug('Modify form is valid')
				transaction=Transaction.objects.get(pk=int(modifyForm.cleaned_data.get('transaction')))
				newTitle=modifyForm.cleaned_data.get('title')
				newType=modifyForm.cleaned_data.get('tag')
				logging.debug('new tag: '+newType)
				newComment=modifyForm.cleaned_data.get('comment')
				logging.debug("entered title is: "+newTitle)
				if newTitle!="":
					transaction.title=newTitle
				transaction.trans_type=newType
				if newComment!="":
					newComment=user.user_name+":\n"+newComment
					oldComm=transaction.comments
					transaction.comments=oldComm+newComment
				transaction.save()
			else:
				modifyForm=ModifyTransactionForm()
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

	return render(request, 'dashboard/activity_page.html',{'user':user,'transactions':transactions, 'modifyForm':modifyForm,"transForm":transactionForm,"trType":transFormType})
