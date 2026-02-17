from django.test import TestCase
from ...models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class UserModelTest(TestCase):
    
    def test_create_user(self):
        user = User.objects.create(
            username = 'testusername',
            email = 'something@ideacloud.com',
            password = 'idea123',
            description = 'some texts',
            created_on = '2026-02-19',
            
        )
        
        self.assertEqual(user.username, 'testusername')
        self.assertEqual(user.email, 'something@ideacloud.com')
        self.assertEqual(user.password, 'idea123')
        self.assertEqual(user.description, 'some texts')
        self.assertEqual(user.created_on, '2026-02-19')