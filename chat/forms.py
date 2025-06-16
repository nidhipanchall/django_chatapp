from django import forms
from .models import Room

class RoomJoinForm(forms.Form):
    room_name = forms.CharField(max_length=255)
