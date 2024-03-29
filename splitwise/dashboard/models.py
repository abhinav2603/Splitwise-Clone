from django.db import models
from django.contrib.auth.models import User as Duser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.forms import ModelForm

# Create your models here.
class User(models.Model):
	user_name=models.CharField(max_length=50)
	email=models.EmailField(max_length=50, blank = True)
	friends = models.ManyToManyField("self",blank=True)
	dp=models.ImageField(upload_to='profile_pic',default='profile_pic/default.png')
	def __str__(self):
		return self.user_name
#class Friends(models.Model):
#	friend1=models.ForeignKey(User,on_delete=models.CASCADE,related_name='User 1')
#	friend2=models.ForeignKey(User,on_delete=models.CASCADE,related_name='User 2')
#	class Meta:
#		unique_together=(('friend1','friend2'),)

class Profile(models.Model):
	user = models.OneToOneField(Duser, on_delete=models.CASCADE)
	bio = models.TextField(max_length=500, blank=True)
	image = models.ImageField(max_length=100,blank=True)
	location = models.CharField(max_length=30, blank=True)
	#birth_date = models.DateField(null=True, blank=True)

class Group(models.Model):
	group_name=models.CharField(max_length=20)
	group_id=models.IntegerField(default=0)
	users=models.ManyToManyField(User)
	def __str__(self):
		return self.group_name


class Transaction(models.Model):
	title=models.CharField(max_length=140)
	trans_type=models.CharField(max_length=10)
	date=models.DateTimeField()
	group=models.ForeignKey(Group,on_delete=models.CASCADE,default=1)
	participants=models.ManyToManyField(User)
	comments=models.CharField(max_length=1000, blank=True)
	def __str__(self):
		return self.title

class TransactionDetail(models.Model):
	trans=models.ForeignKey(Transaction,on_delete=models.CASCADE)
	creditor=models.ForeignKey(User,on_delete=models.CASCADE,related_name="transaction_creditor")
	debitor=models.ForeignKey(User,on_delete=models.CASCADE,related_name="transaction_debitor")
	lent=models.FloatField()
	class Meta:
		unique_together=(('trans','creditor','debitor'),)



class NewGroupForm(forms.ModelForm):
	def __init__(self,*args,**kwargs): # initializing your form in other words loading it
		user_id=kwargs.pop('user_id')
		super(NewGroupForm, self).__init__(*args, **kwargs)
		user = User.objects.get(pk=user_id) # taking user_id out of the querylist
		self.fields['users'] = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=user.friends.all())
	class Meta:
		model=Group
		fields = ['group_name', 'users']

class DateRangeForm(forms.Form):
	Start_Date=forms.DateTimeField(widget=forms.SelectDateWidget())
	End_Date=forms.DateTimeField(widget=forms.SelectDateWidget())

class UpdatedpForm(forms.Form):
	file=forms.FileField()
	#class Meta:
	#	model=User
	#	fields=['dp']

class UploadFileForm(forms.Form):
    file = forms.ImageField()
