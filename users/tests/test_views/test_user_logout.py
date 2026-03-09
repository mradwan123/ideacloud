from django.test import TestCase
from django.contrib.auth import get_user_model
# from serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()

class UserLoginTestAPIView(TestCase):
    """
    Docstring for UserTestAPIView:
    Creates setup with several users, admin, tokens, client, url.
    Test for login view with POST requests.

    """

    def setUp(self):

        # Setting up different users, different roles
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass1',
            email='test1@test.com',
        )

        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass2',
            email='test2@test.com',
        )

        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@email.com'
        )

        # Set up user tokens
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.admin_token = Token.objects.create(user=self.admin)

        self.client = APIClient()

        self.url = reverse('users:logout')

    def test_user_logout_success(self):

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        data = {
            'username': 'testuser1',
            'password': 'testpass1'
        }

        response = self.client.delete(self.url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            msg=f"Expected 204, got {response.status_code}: {response.content}",
        )

    def test_fail_user_logout_no_authentication(self):

        self.client.credentials()
        data = {
            'username': 'testuser1',
            'password': 'testpass1'
        }

        response = self.client.delete(self.url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            msg=f"Expected 401, got {response.status_code}: {response.content}",
        )
        self.assertIn("User not authenticated", str(response.data['error']))
