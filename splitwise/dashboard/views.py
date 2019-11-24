from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import User as myUser, Group as myGroup, Transaction, TransactionDetail, UpdatedpForm, UploadFileForm
from .forms import RegisterForm
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

def personal_page(request):
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

	return render(request,'dashboard/personal_page.html',{'user':user,'nonfriend':nonfriend,'mydict':d});

def friend_page(request,friend_id):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	friend=get_object_or_404(myUser, pk=friend_id)
	transactions=Transaction.objects.filter(participants__in=[user]).filter(participants__in=[friend])
	d=dict()
	state='settled'
	for transaction in transactions:
		d[transaction]=0
	for transaction in transactions:
		for transdet in transaction.transactiondetail_set.all():
			messages.info(request,f"{transdet.lent} {transdet.creditor}")
			credit=transdet.creditor
			debit=transdet.debitor
			lent=transdet.lent
			if credit == user:
				d[transaction]=d[transaction]+lent
			elif debit == user:
				d[transaction]=d[transaction]-lent

	for k,v in d.items():
		if v != 0:
			state='unsettled'
			break

	return render(request,'dashboard/friend_page.html',{
		'user':user,
		'friend':friend,
		'transactions':transactions,
		'mydict':d,
		'state':state})

def settleUp(request,friend_id):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	friend=get_object_or_404(myUser, pk=friend_id)
	transactions=Transaction.objects.filter(participants__in=[user]).filter(participants__in=[friend])
	d=dict()
	for transaction in transactions:
		d[transaction]=0
	for transaction in transactions:
		for transdet in transaction.transactiondetail_set.all():
			messages.info(request,f"{transdet.lent} {transdet.creditor}")
			credit=transdet.creditor
			debit=transdet.debitor
			lent=transdet.lent
			if credit == user:
				d[transaction]=d[transaction]+lent
			elif debit == user:
				d[transaction]=d[transaction]-lent

	for k,v in d.items():
		if v > 0:
			newtrans=Transaction(group=k.group,title='Settled Up',trans_type='SettleUp',date=today)
			newtrans.save()
			newtrans.participants.add(user)
			newtrans.participants.add(friend)
			newtrans.save()
			newtransdet=TransactionDetail(trans=newtrans,creditor=friend,debitor=user,lent=v)
			newtransdet.save()
		elif v < 0:
			newtrans=Transaction(group=k.group,title='Settled Up',trans_type='SettleUp',date=today)
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
	return render(request,'dashboard/pers_group.html',{'user':user});

def addfriend(request,name):
	user_id=request.user.id
	user=get_object_or_404(myUser, pk=user_id)
	frnd=get_object_or_404(myUser, user_name=name)
	user.friends.add(frnd)
	return redirect('dashboard:dashboard')

def userprofile(request):
	user_id = request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	return render(request,'dashboard/profile.html',{'user':user})


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

	
