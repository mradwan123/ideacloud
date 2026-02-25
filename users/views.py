from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import User
from rest_framework import status
from .serializers import UserSerializer
from .permissions import CanUpdateUser, IsAdminOrUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404


User = get_user_model()

class UserAPIView(APIView):
    """
    GET/POST requests with no authentication required.
    - GET request only IsAdminUser() gets list of users with all details.
    - POST request used for new user registration.
    """
    
    def get(self, request, user_id):
        '''GET list of all users. Only admin can see list of all user details. Admin verified through user_id'''
          # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        permission = IsAdminUser()
        if not permission.has_object_permission(request, self, user_id):
            return Response({'error': 'User does not have permission.'}, status.HTTP_403_FORBIDDEN)
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    
    def post(self, request):
        '''New user registration. No authentication or permissions.'''
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
            return Response({'error':'Username and password required.'}, status=400)
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({'Error': 'Invalid username and password'}, status=401)
        
        token = Token.objects.filter(user=user)
        if token:
            token[0].delete()
        token = Token.objects.create(user=user)
        
        return Response({'token': token.key, 'user_id': user.id}, status=200)

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
                return Response({'detail':'Token Deleted. User logged out.'}, status=204)
        return Response({'error': 'User not authenticated'}, status=401)
    
class UserDetailView(APIView):
    """
    GET/PUT/PATCH/DELETE requests.
    Class view with authentication and permission classes stated.
    Checks is user exists with get_user() before proceeding with request.
    """
    
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated, IsAuthenticatedOrReadOnly]
    
    def get_user(self, user_id):
        '''Helper method to get user or return None'''
        return get_object_or_404(User, pk=user_id)
    
    def get(self, request, user_id):
        '''GET single user's details from user_id'''
        user = self.get_user(user_id)
        serializer = UserSerializer(user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response({'error': 'User does not exist'}, status=404)
    
    def patch(self, request, user_id):
        '''Edit partially user details'''
        user = self.get_user(user_id)
        if not permission_classes.has_permission(request, None):
            return Response({'error': 'Authentication required'}, status=401)
        permission = CanUpdateUser()
        if not permission.has_object_permission(request, self, user):
            return Response({'error': 'User does not have permission.'}, status=403)
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
        
    def put(self, request, user_id):
        '''Edit user's details'''
        user = self.get_user(user_id)
        if not permission_classes.has_permission(request, None):
            return Response({'error': 'Authentication required'}, status=401)
        permission = CanUpdateUser()
        if not permission.has_object_permission(request, self, user):
            return Response({'error': 'User does not have permission.'}, status=403)
        
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
        
    def delete(self, request, user_id):
        '''Delete user. Either by Admin or User.'''
        user = self.get_user(user_id)
        if not permission_classes.has_permission(request, None):
            return Response({'error': 'Authentication required'}, status=401)
        permission = IsAdminOrUser()
        user.delete()
        return Response({'detail': 'User deleted successfully'}, status=204)
        