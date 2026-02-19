from django.urls import path
from .views import test_view


app_name = "users"
urlpatterns = [
    path("test/", test_view, name="test"),
]
