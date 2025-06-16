from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # homepage with room form
    path('<str:room_name>/', views.room, name='room'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
]
