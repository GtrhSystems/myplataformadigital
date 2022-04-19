from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('marketplace/get-packages-socket', consumers.PackagesConsumer.as_asgi()),
]