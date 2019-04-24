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
    path('update/<int:poll_id>', views.update, name='update_poll'),

    path('delete/<int:question_id>', views.delete_question, name='delete_question'),
    path('<int:question_id>/add-choice', views.add_choice, name='add_choice'),
    path('api/<int:question_id>/add-choice', views.add_choice_api, name='add_choice_api'),
]