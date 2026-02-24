from django.test import TestCase
from django.contrib.auth import get_user_model
from projects.models import ProjectIdea, ImageProject, ProjectIdeaComment, Tag
from projects.serializers.serializer_project_idea_serializer import ProjectIdeaSerializer

User = get_user_model()


class ProjectIdeaSerializerTests(TestCase):
    def setUp(self):
        # create test user
        self.user = User.objects.create_user(username="test_user", password="password")
        # create test project idea
        self.project_idea = ProjectIdea.objects.create(
            title="test project idea",
            author=self.user,
            description="descriptive text"
        )
        # create test tag
        self.tag = Tag.objects.create(name="python")
        # create test image object
        self.image = ImageProject.objects.create(
            project_idea=self.project_idea,
            image="project_images/test.jpg"
        )
        # create test comment
        self.comment = ProjectIdeaComment.objects.create(
            user=self.user,
            project_idea=self.project_idea,
            content="Nice Idea!"
        )

    def test_serializer_contains_all_fields(self):
        """Verify that all fields are returned correctly"""
        serializer = ProjectIdeaSerializer(instance=self.project_idea)
        data = serializer.data

        expected_fields = {"id", "title", "author", "description", "created_on", "tags", "likes", "images_projects", "project_idea_comments"}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_to_representation_titles_the_title(self):
        """Verify that title is converted to a titled version in representation"""
        serializer = ProjectIdeaSerializer(instance=self.project_idea)
        # original title: title="test project idea"
        self.assertEqual(serializer.data['title'], "Test Project Idea")

    def test_to_internal_value_strips_whitespace(self):
        """Verify that whitespace are stripped from input"""
        data = {
            "title": "   Spaced Title   ",
            "description": "   Spaced description   ",
            "tags": [self.tag.id],
            "likes": [self.user.id]
        }

        serializer = ProjectIdeaSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.error_messages)
        # check the internal value "validated_data"
        self.assertEqual(serializer.validated_data['title'], "Spaced Title")
        self.assertEqual(serializer.validated_data['description'], "Spaced description")

    def test_profanity_validator_raises_error(self):
        """Verify that the ProfanityValidator blocks profanity, when called from project_idea_serializer"""
        data = {
            "title": "This Title Sucks",
            "description": "description",
            "tags": [self.tag.id],
            "likes": [self.user.id]
        }

        serializer = ProjectIdeaSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    # TODO check if the author representation works