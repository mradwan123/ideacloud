from django.test import TestCase
from django.contrib.auth import get_user_model
from projects.models import ProjectIdea, ProjectIdeaComment
from projects.serializers.serializer_project_idea_comment import ProjectIdeaCommentSerializer
User = get_user_model()
class ProjectIdeaCommentTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="ali", password="12345")
        # Create a test project idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test Project",
            description="Test description",

        )
        # Comment data for testing
        self.comment_data = {
            "user": self.user.id,
            "project_idea": self.project_idea.id,
            "content": "This is a test"
        }

    def test_serializer_valid(self):
        # Create serializer with the test data
        serializer = ProjectIdeaCommentSerializer(data=self.comment_data)
        # Print errors if serializer is invalid (optional, helpful for debugging)
        if not serializer.is_valid():
            print(serializer.errors)
        # Check that the serializer is valid
        self.assertTrue(serializer.is_valid())

    def test_serializer_create(self):
        # Create serializer and save the comment
        serializer = ProjectIdeaCommentSerializer(data=self.comment_data)
        if serializer.is_valid():
            comment = serializer.save()
            # Verify the saved comment data
            self.assertEqual(comment.content, self.comment_data["content"])
            self.assertEqual(comment.user, self.user)
            self.assertEqual(comment.project_idea, self.project_idea)
