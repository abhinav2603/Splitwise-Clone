from django.db import models

# Create your models here.
class User(models.Model):
	user_name=models.CharField(max_length=50)
	friends = models.ManyToManyField("self",blank=True)
	def __str__(self):
		return self.user_name
#class Friends(models.Model):
#	friend1=models.ForeignKey(User,on_delete=models.CASCADE,related_name='User 1')
#	friend2=models.ForeignKey(User,on_delete=models.CASCADE,related_name='User 2')
#	class Meta:
#		unique_together=(('friend1','friend2'),)

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
	def __str__(self):
		return self.title

class TransactionDetail(models.Model):
	trans=models.ForeignKey(Transaction,on_delete=models.CASCADE)
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	lent=models.FloatField()
	class Meta:
		unique_together=(('trans','user'),)