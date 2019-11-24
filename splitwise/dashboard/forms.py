from django import forms
from django.forms import ModelForm

from .models import Profile,Transaction,User as myUser,Group

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class DateInput(forms.DateInput):
    input_type = 'date'


class TransactionForm(forms.ModelForm):
	class Meta:
		model=Transaction
		fields=['title','trans_type','date','group']
		widgets={'date':forms.SelectDateWidget(),}

	def __init__(self,*args,**kwargs): # initializing your form in other words loading it
		user_id=kwargs.pop('user_id')
		super(TransactionForm, self).__init__(*args, **kwargs)
		var = myUser.objects.get(pk=user_id)
		types=[ ('Movies','Movies'),('Food','Food'),('Housing','Housing'),('Travel','Travel'),('Others','Others')]
		self.fields['group']=forms.ModelChoiceField(queryset=var.group_set.all())
		#self.fields['participants']=forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=var.friends.all())
		self.fields['trans_type']=forms.ChoiceField(choices=types)

	#transTitle=forms.CharField(label='Transaction Title', max_length=100)
	
	#transType=forms.ChoiceField(label='Kind of transaction',choices=types)
	#date=forms.DateTimeField(label='Date',input_formats=['%m/%d/%Y'],widget=forms.SelectDateWidget())
	#var=User.objects.get(pk=1)
	#group=forms.ModelChoiceField(queryset=var.group_set.all())

class TransactionParticipantsForm(forms.Form):
	def __init__(self,*args,**kwargs):
		user_id=kwargs.pop('user_id')
		group_id=kwargs.pop('group_id')
		user=myUser.objects.get(pk=user_id)
		group=Group.objects.get(group_id=group_id)
		super(TransactionParticipantsForm, self).__init__(*args, **kwargs)
		if group==Group.objects.get(group_id=0):
			#in no group
			self.fields['participants']=forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(),queryset=user.friends.all())
		else:
			self.fields['participants']=forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(),queryset=group.users.all())

class TransactionDetailForm(forms.Form):
	amount=forms.FloatField(label='Total amount paid',min_value=0)
	def __init__(self,*args,**kwargs):
		self.participants_list=kwargs.pop('participants_list')
		super(TransactionDetailForm, self).__init__(*args, **kwargs)
		for participant in self.participants_list:
			self.fields[str(participant.id)+'gave']=forms.FloatField(label=participant.user_name+' gave')
			self.fields[str(participant.id)+'share']=forms.FloatField(label=participant.user_name+' share')

	def clean(self):
		form_data=super().clean()
		#form_data=self.cleaned_data
		total_given=0
		total_share=0
		participants_ids=[]
		for participant in self.participants_list:
			participants_ids.append(participant.id)

		for i in participants_ids:
			total_given=total_given+form_data[str(i)+'gave']
			total_share=total_share+form_data[str(i)+'share']

		if total_given!=form_data['amount']:
			raise forms.ValidationError('Total amount given by participants don\'t match')
			#self._errors['amount']=["Total amount given by participants don't match"]
		if total_share!=form_data['amount']:
			raise forms.ValidationError('Total share of participants don\'t match')
			#self._errors['amount']=["Total share of participants don't match"]

		return form_data


class ModifyTransactionForm(forms.Form):
	title=forms.CharField(label='Enter a new title, or leave empty',max_length=140,required=False)
	types=[ ('Movies','Movies'),('Food','Food'),('Housing','Housing'),('Travel','Travel'),('Others','Others')]
	tag=forms.ChoiceField(choices=types)
	comment=forms.CharField(label='Add a comment',max_length=150,required=False)
	transaction=forms.IntegerField(required=False,widget=forms.HiddenInput())
	#def __init__(self,*args,**kwargs):
	#	trans_id=kwargs.pop('trans_id')
	#	trans=Transaction.objects.get(pk=trans_id)
	#	super(TransactionDetailForm, self).__init__(*args, **kwargs)
	#	self.fields['transaction']=

class GroupSettleForm(forms.Form):
	def __init__(self,*args,**kwargs):
		group_id=kwargs.pop('group_id')
		user_id=kwargs.pop('user_id')
		group=Group.objects.get(group_id=group_id)
		super(GroupSettleForm, self).__init__(*args, **kwargs)
		self.fields['users']=forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(),queryset=group.users.exclude(pk=user_id))


