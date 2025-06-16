from django.db import models

class Message(models.Model):
    username = models.CharField(max_length=255)
    room = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.username}: {self.content}"

class UserActivity(models.Model):
    username = models.CharField(max_length=100, unique=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.last_seen}"
