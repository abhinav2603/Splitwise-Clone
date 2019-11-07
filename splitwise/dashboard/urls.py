from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path("logout", views.logout_request, name="logout"),
    path("login", views.login_request, name="login"),
    path('dashboard',views.personal_page,name='dashboard'),
    path('friends/<int:friend_id>',views.friend_page,name='friend')
]