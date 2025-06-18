from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer
from django.shortcuts import render

class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        room = self.request.query_params.get('room')
        if room:
            return Message.objects.filter(room=room).order_by('timestamp')
        return Message.objects.all().order_by('timestamp')

def chat_room(request, room_name):
    return render(request, 'chat/room.html', {'room_name': room_name})

