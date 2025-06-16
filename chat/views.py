from django.shortcuts import render

def index(request):
    return render(request, 'chat/index.html')
    # path('<str:room_name>/', views.room, name='room'),

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })

def chat_room(request, room_name):
    return render(request, 'chat_room.html', {'room_name': room_name})