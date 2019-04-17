from django.urls import path

from polls import views

urlpatterns = [
    path('index/', views.index, name="index"),
    path('detail/<int:poll_id>', views.detail, name="poll_detail"),
    path('create/', views.create, name='create_poll'),
    path('login/', views.my_login, name='login'),
    path('logout/', views.my_logout, name='logout'),
    path('detail/<int:poll_id>/comments/', views.comment, name='comment'),
    path('change_password/', views.changePassword, name='changepassword'),
    path('register/', views.my_register, name='register'),

]