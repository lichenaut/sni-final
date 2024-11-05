from django.urls import path
from .views import Videoize

urlpatterns = [
    path("videoize/", Videoize.as_view(), name="videoize"),
]
