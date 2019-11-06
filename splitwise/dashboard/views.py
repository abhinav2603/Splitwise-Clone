from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import User

# Create your views here.
def index(request):
	return HttpResponse("Dashboard");

def personal_page(request,user_id):
	user=get_object_or_404(User, pk=user_id)
	return render(request,'dashboard/pers_page.html',{'user':user});