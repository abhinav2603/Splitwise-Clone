from django.db import models

# Create your models here.
class User(models.Model):
	user_name=models.CharField(max_length=50)
	friends = models.ManyToManyField("self")

#class Friends(models.Model):
#	friend1=models.ForeignKey(User,on_delete=models.CASCADE,related_name='User 1')
#	friend2=models.ForeignKey(User,on_delete=models.CASCADE,related_name='User 2')
#	class Meta:
#		unique_together=(('friend1','friend2'),)

class Groups(models.Model):
	group_id=models.IntegerField(default=0)
	user_id=models.ForeignKey(User,on_delete=models.CASCADE)
	class Meta:
		unique_together=(('group_id','user_id'),)

class Transaction(models.Model):
	trans_type=models.CharField(max_length=10)
	date=models.DateTimeField()

class TransactionDetail(models.Model):
	trans_id=models.ForeignKey(Transaction,on_delete=models.CASCADE)
	user_id=models.ForeignKey(User,on_delete=models.CASCADE)
	group_id=models.ForeignKey(Groups,on_delete=models.CASCADE)
	lent=models.FloatField()
	class Meta:
		unique_together=(('trans_id','user_id'),)