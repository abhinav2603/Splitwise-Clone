from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
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
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from django.db.models import Q

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
	return render(request,'dashboard/personal_page.html',{'user':user,'nonfriend':nonfriend});

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

def insights(request):
	user_id = request.user.id
	user = get_object_or_404(myUser, pk=user_id)
	group = get_list_or_404(myGroup, users__in = [user])
	#transaction = Transaction.objects.filter(participants__in=[user]).order_by('date')
	transactiondetail = TransactionDetail.objects.filter(Q(creditor__in = [user]) | Q(debitor__in = [user])).order_by('trans__date')

	##############################################	
	dictlst = []
	i = 0
	j = 0
	datelst = []
	typlst = []
	for row in transactiondetail:
		dat = row.trans.date
		dat = dat.strftime('%Y-%m-%d')
		datelst.append(dat)
		j = j + 1
		mydic={}
		temp = row.trans.trans_type
		#rowtd = row.transactiondetail_set.all()
		money = row.lent
		p1 = row.creditor
		p2 = row.debitor
		if temp in mydic.keys():
			if (p1==user):
				mydic[temp] = mydic[temp] + money
			else:
				mydic[temp] = mydic[temp] - money
		else:
			i = i + 1
			typlst.append(temp)
			if (p1==user):
				mydic[temp] = money
			else:
				mydic[temp] = -1*money
		dictlst.append((dat,mydic))
	tlst=[]
	for w in range(0,i):
		mylst = {}
		typ = typlst[w]
		for z in range(0,j):
			tempdic = dictlst[z][1]
			if typ in tempdic.keys():
				mylst[dictlst[z][0]]=tempdic[typ]
		tlst.append(mylst)

	##############################################
	mydict = {}
	for row in transactiondetail:
		temp = row.trans.trans_type
		money = row.lent
		p1 = row.creditor
		p2 = row.debitor
		if temp in mydict.keys():
			if (p1==user):
				mydict[temp] = mydict[temp] + money
			else:
				mydict[temp] = mydict[temp] - money
		else:
			if (p1==user):
				mydict[temp] = money
			else:
				mydict[temp] = -1*money
	pielabels=mydict.keys()
	pievalues=mydict.values()
	
	##############################################
	mydict1 = {}
	for row in transactiondetail:
		money = row.lent
		p1 = row.creditor
		p2 = row.debitor
		if (p1==user):
			if p2 in mydict1.keys():
				mydict1[p2] = mydict1[p2] + money
			else:
				mydict1[p2]=money
		else:
			if p1 in mydict1.keys():
				mydict1[p1] = mydict1[p1] - money
			else:
				mydict1[p1]=-1*money
	pielabels1=mydict1.keys()
	pievalues1=mydict1.values()

	##############################################
	mydicto = {}
	mydictl = {}
	for row in transactiondetail:
		#rowtd = row.transactiondetail_set.all()
		group = row.trans.group.group_name
		p1 = row.creditor
		p2 = row.debitor
		money = row.lent
		if (p1==user):
			if group not in mydictl.keys():
				mydictl[group]=0
			if group in mydicto.keys():
				mydicto[group] = mydicto[group] + money
			else:
				mydicto[group] = money
		else:
			if group not in mydicto.keys():
				mydicto[group]=0
			if group in mydictl.keys():
				mydictl[group] = mydictl[group] + money
			else:
				mydictl[group] = money
	'''for row in transactiondetail:
		group = row.trans.group.group_name
		p1 = row.creditor
		p2 = row.debitor
		if (p1==user):
			if group not in mydictl.keys():
				mydictl[group]=0
		if (p2==user):
			if group not in mydicto.keys():
				mydicto[group]=0
	sorted(mydicto.keys())
	sorted(mydictl.keys())'''
	groups = mydicto.keys()
	owes = mydicto.values()
	lents = mydictl.values()
	l = len(groups)
	widthg = 0.20
	ind = np.arange(l)
	
	##############################################
	mydictof = {}
	mydictlf = {}
	for row in transactiondetail:
		p1 = row.creditor
		p2 = row.debitor
		money = row.lent
		if (p1==user):
			if p2 not in mydictlf.keys():
				mydictlf[p2]=0
			if p2 in mydictof.keys():
				mydictof[p2] = mydictof[p2] + money
			else:
				mydictof[p2] = money
		else:
			if p1 not in mydictof.keys():
				mydictof[p1]=0
			if p1 in mydictlf.keys():
				mydictlf[p1] = mydictlf[p1] + money
			else:
				mydictlf[p1] = money
	'''for row in transactiondetail:
		p1 = row.creditor
		p2 = row.debitor
		money = row.lent
		if (p1==user):
			if p2 not in mydictlf.keys():
				mydictlf[p2]=0
		if (p2==user):
			if p1 not in mydictof.keys():
				mydictof[p1]=0
	sorted(mydictof.keys())
	sorted(mydictlf.keys())'''
	friends = mydictof.keys()
	owesf = mydictof.values()
	lentsf = mydictlf.values()
	lf = len(friends)
	widthf = 0.20
	indf = np.arange(lf)

	##############################################

	with PdfPages(r'insights.pdf') as export_pdf:
		###############################
		'''
		for typ in range(0, i):
			plt.plot(np.array(tlst[typ].keys()), np.array(tlst[typ].values()))
		plt.legend()
		plt.title('Time Series Plot')
		plt.xlabel('Date and Time')
		plt.ylabel('Expenditure')
		export_pdf.savefig()
		plt.close()
		'''

		###############################
		fig1, ax1 = plt.subplots()
		ax1.pie(pievalues, labels=pielabels,autopct='%.2f', startangle=90)
		ax1.axis('equal')
		export_pdf.savefig(fig1)
		plt.close()

		###############################
		fig2, ax2 = plt.subplots()
		ax2.pie(pievalues1, labels=pielabels1,autopct='%.2f', startangle=90)
		ax2.axis('equal')
		export_pdf.savefig(fig2)
		plt.close()
		
		###############################
		
		p1 = plt.bar(ind, owes, width = widthg)
		p2 = plt.bar(ind, lents, width = widthg)
		plt.xlabel('Groups')
		plt.ylabel('Money')
		plt.title('Money owed and lent in a group')
		plt.xticks(ind, groups)
		#plt.legend((p1[0], p2[0]), ('Owing', 'Lent'))
		export_pdf.savefig()
		plt.close()

		###############################	
		p1f = plt.bar(indf, owesf, width = widthf)
		p2f = plt.bar(indf, lentsf, width = widthf)
		plt.xlabel('Friends')
		plt.ylabel('Money')
		plt.title('Money owed and lent among friends')
		plt.xticks(indf, friends)
		#plt.legend((p1f[0], p2f[0]), ('Owing', 'Lent'))
		export_pdf.savefig()
		plt.close()

	return render(request,'dashboard/insights.html',{'user':user}); 

def pdf_view(request):
	with open('insights.pdf', 'rb') as pdf:
		response = HttpResponse(pdf.read(), content_type='application/pdf')
		response['Content-Disposition'] = 'inline;filename=insights.pdf'
		return response