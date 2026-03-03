from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()

class UserDetailTestAPIView(TestCase):
    """
    Docstring for UserTestAPIView: GET/PUT/PATCH/DELETE requests for user detail views 
    Take from permissions: IsAdminOrUser, CanUpdateUser
    Creates setup with several users, admin, tokens, client, url.
    - User only can GET details. Admin cannot.
    - User that does not exist fails test.
    """

    def setUp(self):

        # Setting up different users, different roles
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass1',
            email='test1@test.com',
            description='test desc'
        )

        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass2',
            email='test2@test.com',
            description='test desc'
        )

        self.admin= User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@email.com',
            description='test decr',
            is_staff=True,
            is_superuser=True,
       )

        #Set up user tokens
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.admin_token = Token.objects.create(user=self.admin) 

        self.client = APIClient()

        self.url = reverse('users:user-detail', args=[self.user1.pk])
        
#----------------- User only can GET request for existing User details  ------------------------------
        
    def test_success_user_get_single_user_own_detail_as_user(self):
        '''User can retrieve own details. User authenticated.'''

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")

        response= self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_fail_admin_get_user_details(self):
        '''Admin cannot retrieve a single user's details.'''

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        response= self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    
    def test_fail_admin_get_user_that_does_not_exist(self):
        '''Admin cannot retrieve user details for user that does not exist. 
        Addded 99999 large user_id that wont exist'''
        self.url = reverse('users:user-detail', args=[99999999]) 

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        response= self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('No User matches the given query', response.data['detail'])
    
    
#TODO sample tests below to adjust for this model. Delete unwanted tests.
        
#     def test_fail_user_get_different_user_detail(self):
#         '''User cannot retrieve other user details. Checking IsAdminOrUser.'''

#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token2.key}")

#         response= self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertIn('Permission to read does not exist', response.data['error'])

        
    

#------------------------ user account DELETE ---------------------

    def test_delete_user_by_user(self):
        '''User attempts to delete own account'''

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        url= reverse('users:user-detail', args=[self.user1.pk])

        response =self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            msg=f"Expected 204, got {response.status_code}: {response.content}",
        )

#     def test_fail_delete_user_by_other_user(self):
#         '''User fails attempt to delete different user account account'''

#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
#         url= reverse('users-apis:user-detail', args=[self.user2.pk])

#         response =self.client.delete(url)

#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
#             msg=f"Expected 401, got {response.status_code}: {response.content}",
#         )
        
#         self.assertIn('permission', str(response.data['error']).lower())
      
#         self.assertIn('permission', str(response.data['error']).lower())
        
#     def test_success_delete_user_by_admin(self):
#         '''Admin attempts to delete user account'''
        
#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
#         url= reverse('users-apis:user-detail', args=[self.user1.pk])
    
#         response =self.client.delete(url)

#         self.assertEqual(
#             response.status_code,
#             status.HTTP_204_NO_CONTENT,
#             msg=f"Expected 204, got {response.status_code}: {response.content}",
#         )
        

# #------------------------ user edit account with PATCH request ---------------------

    def test_update_user_account_by_user(self):
        '''User attempts to partially update own account. PATCH request'''

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        url= reverse('users:user-detail', args=[self.user1.pk])

        updated_data= {
            'username':'testusernameee'
        }
        response =self.client.patch(
                    url, updated_data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"Expected 200, got {response.status_code}: {response.content}",
        )
        
#     def test_update_user_account_by_different_user(self):
#         '''User attempts to partiallu update someone else's account. PATCH request. Fails miserably'''

#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token2.key}")
#         url= reverse('users-apis:user-detail', args=[self.user1.pk])

#         updated_data= {
#             'username':'testusernameee'
#         }
#         response =self.client.patch(
#                     url, updated_data, format='json')

#         self.assertEqual(
#             response.status_code,
#             status.HTTP_403_FORBIDDEN,
#             msg=f"Expected 403, got {response.status_code}: {response.content}",
#         )
        
# #------------------------ user edit account with PUT request ---------------------

    def test_success_update_user_account_by_user(self):
        '''User attempts to full update own account. PUT request'''

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        url= reverse('users:user-detail', args=[self.user1.pk])

        updated_data= {
            'email':'test@test.com',
            'username':'testuser12',
            'password':'Testpass123',
            'description': 'tests desc'
        }
        response =self.client.put(
                    url, updated_data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"Expected 200, got {response.status_code}: {response.content}",
        )
        
#     def test_success_update_user_account_by_user_without_password(self):
#         '''
#         User attempts to update own account without changes to password. 
#         Password not required. PUT request'''

#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
#         url= reverse('users-apis:user-detail', args=[self.user1.pk])

#         updated_data= {
#             'email':'test@test.com',
#             'username':'testusernameee',
#             # 'password':'newpassword'
#         }
#         response =self.client.put(
#                     url, updated_data, format='json')

#         self.assertEqual(
#             response.status_code,
#             status.HTTP_200_OK,
#             msg=f"Expected 200, got {response.status_code}: {response.content}",
#         )
