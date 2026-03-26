from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import UserSerializer
from .permissions import CanUpdateUser, IsAdminOrUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.core.cache import cache

User = get_user_model()

class UserAPIView(APIView):
    """
    GET/POST requests with no authentication required.
    - GET request only IsAdminUser() gets list of users with all details.
    - POST request used for new user registration.
    """

    authentication_classes = [TokenAuthentication,]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAdminUser()]  # only admin can list users
        if self.request.method == "POST":
            return [AllowAny()]  # anyone can create user
        return super().get_permissions()

    def get(self, request):
        """
        GET list of all users. Only admin can see list of all user details.
        - Checks for authentication.
        - Admin verified through user_id
        """
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check cache first
        cached = cache.get("admin:all_users")
        if cached:
            return Response(cached, status=status.HTTP_200_OK)
        
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        cache.set("admin:all_users", serializer.data, timeout=60 * 5)  # 5 min TTL

        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request):
        '''New user registration. No authentication or permissions.

        The image data has to be send as a jpg image in base64 byte format.
        '''
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.data, status=400)

class LoginView(APIView):
    """
    LoginView uses username/password.
    - Checks if username/password provided by user.
    - Authenticated username/password.
    - Token provided upon login, deletes old token if exists.
    """
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({'error': 'Username and password required.'}, status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'Error': 'Invalid username and password'}, status.HTTP_401_UNAUTHORIZED)

        token = Token.objects.filter(user=user)
        if token:
            token[0].delete()
        token = Token.objects.create(user=user)

        return Response({'token': token.key, 'user_id': user.id}, status.HTTP_200_OK)

class LogoutView(APIView):
    """
    LogoutView check if user is authenticated, find user Token, deletes to log out.
    """

    authentication_classes = [TokenAuthentication,]

    def delete(self, request):

        if request.user.is_authenticated:
            token = Token.objects.filter(user=request.user)
            if token:
                token[0].delete()
                return Response({'detail': 'Token Deleted. User logged out.'}, status.HTTP_204_NO_CONTENT)
        return Response({'error': 'User not authenticated'}, status.HTTP_401_UNAUTHORIZED)

class UserDetailView(APIView):
    """
    GET/PUT/PATCH/DELETE requests.
    Class view with authentication and permission classes stated.
    Checks is user exists with get_user() before proceeding with request.
    """

    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAdminOrUser, CanUpdateUser,]

    def get_user(self, user_id):
        '''Helper method to get user or return None'''
        return get_object_or_404(User, pk=user_id)

    def get(self, request, user_id):
        '''User can GET own user's details from user_id'''

        user = self.get_user(user_id)
        self.check_object_permissions(request, user)

        cache_key = f"user:{user_id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached, status=status.HTTP_200_OK)
        
        serializer = UserSerializer(user)
        cache.set(cache_key, serializer.data, timeout=60 * 10)  # 10 min TTL

        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request, user_id):
        '''User can Edit partially own user details. check_object_permissions().

        The image data has to be send as a jpg image in base64 byte format.
        Recieving NULL (None in python) restores the default image as profile picture.
        '''
        user = self.get_user(user_id)
        self.check_object_permissions(request, user)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete(f"user:{user_id}")       # bust individual cache
            cache.delete("admin:all_users")        # bust list cache
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def put(self, request, user_id):
        '''User can Edit user's details. check_object_permission()

        The image data has to be send as a jpg image in base64 byte format.
        Recieving NULL (None in python) restores the default image as profile picture.
        '''
        user = self.get_user(user_id)
        self.check_object_permissions(request, user)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():

            serializer.save()
            cache.delete(f"user:{user_id}")
            cache.delete("admin:all_users")
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        '''Delete user. Either by Admin or User.'''
        user = self.get_user(user_id)
        self.check_object_permissions(request, user)

        user.delete()
        cache.delete(f"user:{user_id}")
        cache.delete("admin:all_users")
        return Response({'detail': 'User deleted successfully'}, status.HTTP_204_NO_CONTENT)
