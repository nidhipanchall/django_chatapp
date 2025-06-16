"""
ASGI config for chat_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# ✅ Set environment variable BEFORE anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')

# ✅ Setup Django BEFORE importing any models, routing, etc.
django.setup()

# ✅ Safe to import after Django setup
import chat.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        chat.routing.websocket_urlpatterns
    ),
})




