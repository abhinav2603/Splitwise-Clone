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
    #path('accounts/', include('django.contrib.auth.urls')),
    #path('change-password/', auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('account:password_change_done')),name='change_password'),
    path('password', views.change_password, name='changePassword'),
]