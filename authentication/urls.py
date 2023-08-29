# app level api routing
from authentication.views import login
from authentication.views import create_user,list_users,partial_update_user,delete_user,logout_user
from django.urls import path
urlpatterns = [
    path('api/login', login, name='login'),
    path('api/user/create', create_user, name='create'),
    path('api/user/list', list_users, name='list'),
    path('api/update-user/<int:user_id>',partial_update_user, name='update-user'),
    path('api/delete-user/<int:user_id>', delete_user, name='delete-user'),
    path('api/logout', logout_user, name='logout'),
]