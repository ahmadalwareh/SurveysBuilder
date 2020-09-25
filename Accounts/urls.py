from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'Accounts'
urlpatterns = [
    path('update_info', views.update_info, name='update_info'),
    path('create_user', views.create_user, name='create_user'),
    path('change_password', views.change_password, name='change_password'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('test_auth', views.test, name='test'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('change_user_status/<int:user_id>/<int:status>', views.change_user_status, name='change_user_status'),
    path('change_user_privilege/<int:user_id>/<int:status>', views.change_user_privilege, name='change_user_privilege'),
]
