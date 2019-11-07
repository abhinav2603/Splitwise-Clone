from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path("logout", views.logout_request, name="logout"),
    path("login", views.login_request, name="login"),
    path('<int:user_id>',views.personal_page,name='dashboard'),
]