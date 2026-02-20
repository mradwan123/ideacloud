from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import get_user_model
# from .models import User
# from serializers import UserSerializer
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
# from rest_framework.decorators import api_view, authentication_classes, permission_classes


# Create your views here.

def test_view(request):
    User = get_user_model()
    user = User.objects.create_user(username="e", password="a")
    html = f"<img src={user.image.url}>"
    return HttpResponse(html)

# class UserAPIView(APIView):
    
#     def get(self, request):
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)