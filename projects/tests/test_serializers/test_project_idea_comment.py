from django.test import TestCase
from django.contrib.auth.models import User
from projects.models import ProjectIdeaComment
from projects.serializers import ProjectIdeaCommentSerializer

class ProjectIdeaCommentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ali", password="12345")

        self.comment_data = {
         "user": self.user.id,
         "comment_text": "This is a test"
        }
  
    
    def test_serializer_valid(self):
        serializer = ProjectIdeaCommentSerializer(data=self.comment_data)
        self.assertTrue(serializer.is_valid())
        
    def test_serializer_create(self):
        serializer = ProjectIdeaCommentSerializer(data=self.comment_data)
        if serializer.is_valid():
            comment = serializer.save()
            self.assertEqual(comment.comment_text, self.comment_data["comment_text"])
            self.assertEqual(comment.user, self.user)