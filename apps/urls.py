from django.urls import path
from apps.views import home
from apps.chat.views import upload_document, chat

urlpatterns = [
    path("", home, name="home"),
    path("chat/", chat, name="chat"),
    path("upload/", upload_document, name="upload_document"),
]
