from django.urls import path

from polls import views

urlpatterns = [
    path('index/', views.index, name="index"),
    path('detail/<int:poll_id>', views.detail, name="poll_detail"),
]