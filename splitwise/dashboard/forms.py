from django import forms
from django.forms import ModelForm
from .models import Profile,Transaction,User,Group

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio'),('location'),'image',


class DateInput(forms.DateInput):
    input_type = 'date'


class TransactionForm(forms.ModelForm):
	class Meta:
		model=Transaction
		fields=['title','trans_type','date','group','participants']
		widgets={'date':forms.SelectDateWidget(),}

	def __init__(self,*args,**kwargs): # initializing your form in other words loading it
		user_id=kwargs.pop('user_id')
		super(TransactionForm, self).__init__(*args, **kwargs)
		var = User.objects.get(pk=user_id)
		types=[ ('Movies','Movies'),('Food','Food'),('Housing','Housing'),('Travel','Travel'),('Others','Others')]
		self.fields['group']=forms.ModelChoiceField(queryset=var.group_set.all())
		self.fields['participants']=forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=var.friends.all())
		self.fields['trans_type']=forms.ChoiceField(choices=types)

	#transTitle=forms.CharField(label='Transaction Title', max_length=100)
	
	#transType=forms.ChoiceField(label='Kind of transaction',choices=types)
	#date=forms.DateTimeField(label='Date',input_formats=['%m/%d/%Y'],widget=forms.SelectDateWidget())
	#var=User.objects.get(pk=1)
	#group=forms.ModelChoiceField(queryset=var.group_set.all())

class TransactionDetailForm(forms.Form):
	amount=forms.FloatField(label='Total amount paid',min_value=0)
	def __init__(self,*args,**kwargs):
		self.participants_list=kwargs.pop('participants_list')
		super(TransactionDetailForm, self).__init__(*args, **kwargs)
		for participant in self.participants_list:
			self.fields[str(participant.id)+'gave']=forms.FloatField(label=participant.user_name+' gave')
			self.fields[str(participant.id)+'share']=forms.FloatField(label=participant.user_name+' sharev')

	def clean(self):
		form_data=self.cleaned_data
		total_given=0
		total_share=0
		participants_ids=[]
		for participant in self.participants_list:
			participants_ids.append(participant.id)

		for i in participants_ids:
			total_given=total_given+form_data[str(i)+'gave']
			total_share=total_share+form_data[str(i)+'share']

		if total_given!=form_data['amount']:
			self._errors['amount']=["Total amount given by participants don't match"]
		if total_share!=form_data['amount']:
			self._errors['amount']=["Total share of participants don't match"]

		return form_data




