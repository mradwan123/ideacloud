from django.test import TestCase
from ...models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

class UserModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            username = 'testusername',
            email = 'something@ideacloud.com',
            password = 'idea123',
            description = 'some texts',
            created_on = '2026-02-19',   
            )
    
        
    #---- VALIDATION --------------
        self.assertEqual(self.user.username, 'testusername')
        self.assertEqual(self.user.email, 'something@ideacloud.com')
        self.assertEqual(self.user.password, 'idea123')
        self.assertEqual(self.user.description, 'some texts')
        
    def test_created_on_correct_timestamp(self):
        """Verify that timestamps are generated correctly"""
        self.assertIsNotNone(self.user.created_on)
        now = timezone.now()
        # we use AlmostEqual, because we can't compare accurately on a detailed level because the code takes time to run
        self.assertAlmostEqual(
            self.user.created_on,
            now,
            delta=timedelta(minutes=1)
        )