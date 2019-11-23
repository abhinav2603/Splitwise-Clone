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
		self.fields['group']=forms.ModelChoiceField(queryset=var.group_set.all())
		self.fields['participants']=forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=var.friends.all())

	#transTitle=forms.CharField(label='Transaction Title', max_length=100)
	#types=[ ('Movies','Movies'),('Food','Food'),('Housing','Housing'),('Travel','Travel'),('Others','Others')]
	#transType=forms.ChoiceField(label='Kind of transaction',choices=types)
	#date=forms.DateTimeField(label='Date',input_formats=['%m/%d/%Y'],widget=forms.SelectDateWidget())
	#var=User.objects.get(pk=1)
	#group=forms.ModelChoiceField(queryset=var.group_set.all())



