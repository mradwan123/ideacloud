from django.test import TestCase
from django.contrib.auth import get_user_model
from projects.models import ProjectIdea, ProjectComment
from projects.serializers.serializer_project_comment import ProjectCommentSerializer

User = get_user_model()


class ProjectCommentSerializerTests(TestCase):
    def setUp(self):
        # create users
        self.user_author = User.objects.create_user(username="author", password="password")

        # create a project idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test Project Idea",
            description="Test description",
            author=self.user_author
        )

        self.comment_data = {
            "content": "This is a valid comment"
        }

    ### VALID
    ## SERIALIZATION
    def test_serializer_is_valid_with_proper_data(self):
        """Verify that the serializer accepts valid data"""
        serializer = ProjectCommentSerializer(data=self.comment_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_creates_comment_correctly(self):
        """Verify that the serializer saves the comment correctly when views inject fields"""
        serializer = ProjectCommentSerializer(data=self.comment_data)

        if serializer.is_valid():
            comment = serializer.save(author=self.user_author, project_idea=self.project_idea)

            self.assertEqual(comment.content, self.comment_data["content"])
            self.assertEqual(comment.author, self.user_author)
            self.assertEqual(comment.project_idea, self.project_idea)

    def test_serializer_outputs_author_username_instead_of_id(self):
        """Verify that the ReadOnlyField maps the author ID to the username string"""
        comment = ProjectComment.objects.create(
            content="Test mapping",
            author=self.user_author,
            project_idea=self.project_idea
        )

        serializer = ProjectCommentSerializer(comment)
        self.assertEqual(serializer.data["author"], self.user_author.username)

    ### INVALID
    ## VALIDATION
    def test_serializer_invalid_too_long_content(self):
        """Verify that the serializer rejects content that exceeds the max length"""
        invalid_data = {
            "content": "A" * 501
        }

        serializer = ProjectCommentSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("content", serializer.errors)