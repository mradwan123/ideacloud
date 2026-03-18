from django.urls import path
from .views import UserAPIView, LoginView, LogoutView, UserDetailView


app_name = "users"
urlpatterns = [
    path('users/', UserAPIView.as_view(), name='user'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail')
]
