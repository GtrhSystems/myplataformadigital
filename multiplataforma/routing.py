from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('comments/get-comments-socket', consumers.PackagesConsumer.as_asgi()),
]