from django.urls import path
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf.urls import include

app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path("logout", views.logout_request, name="logout"),
    path("login", views.login_request, name="login"),
    path('dashboard',views.personal_page,name='dashboard'),
    path('friends/<int:friend_id>',views.friend_page,name='friend'),
    path('groups',views.my_group,name='all_groups'),
    path('group/<int:group_id>',views.group_page,name='group'),
    path('addfriend/<str:name>',views.addfriend,name='fadd'),
    path('settings',views.userprofile,name='user_profile'),
    path('changepic',views.update_pic,name='update-pic'),
    path('settleup/<int:friend_id>',views.settleUp,name='settleup'),
    path('remove/<int:group_id>',views.delete,name="delete"),
    path('leave/<int:group_id>',views.leave,name='leave'),
    path('password', views.change_password, name='changePassword'),
    path('insights', views.insights, name='insights'),
    path('pdf_view', views.pdf_view, name='pdf_view'),
    path('balance/<int:group_id>',views.balance,name='balance'),
    path('activity',views.activity,name='activity'),
    path('excel',views.some_view,name='xlview'),
]