from django.test import TestCase
from django.contrib.auth import get_user_model

from projects.models import ProjectIdea, ProjectIdeaComment
from projects.serializers.serializer_project_idea_comment import ProjectIdeaCommentSerializer


User = get_user_model()


class ProjectIdeaCommentTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="ali",
            password="12345"
        )

        # Create a test project idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test Project",
            description="Test description"
        )

        # Comment data for testing
        self.comment_data = {
            "user": self.user.id,
            "project_idea": self.project_idea.id,
            "content": "This is a test"
        }

    def test_serializer_valid(self):
        """Serializer should validate correct data."""
        serializer = ProjectIdeaCommentSerializer(data=self.comment_data)

        if not serializer.is_valid():
            print(serializer.errors)

        self.assertTrue(serializer.is_valid())

    def test_serializer_create(self):
        """Serializer should create a comment correctly."""
        serializer = ProjectIdeaCommentSerializer(data=self.comment_data)

        self.assertTrue(serializer.is_valid())

        comment = serializer.save()

        # Verify saved data
        self.assertEqual(comment.content, self.comment_data["content"])
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.project_idea, self.project_idea)