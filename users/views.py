from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import get_user_model

# Create your views here.

def test_view(request):
    User = get_user_model()
    user = User.objects.create_user(username="e", password="a")
    html = f"<img src={user.image.url}>"
    return HttpResponse(html)
