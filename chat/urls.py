from django.urls import path
from . import views

urlpatterns = [
    path('<str:room_name>/', views.chat_room, name='room'),
    path('api/messages/', views.MessageListCreateAPIView.as_view(), name='api_messages'),
    
]
