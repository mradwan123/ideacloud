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

    def test_tags_and_likes_are_saved(self):
        """Verify that M2M IDs are correctly converted to database relations"""
        data = {
            "title": "Title",
            "description": "Description",
            "tags": [self.tag.id],
            "likes": [self.user.id]
        }
        serializer = ProjectIdeaSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        # author is read-only so we pass it here
        project = serializer.save(author=self.user)
        # fetch from DB to ensure the save actually was done
        project.refresh_from_db()

        self.assertEqual(project.tags.count(), 1)
        self.assertEqual(project.likes.count(), 1)

    def test_nested_serializers_presence(self):
        """Verify that the keys for nested serializers exist in the output"""
        serializer = ProjectIdeaSerializer(instance=self.project_idea)

        # we only care that the keys exist and are the right type (list)
        self.assertIsInstance(serializer.data['images_projects'], list)
        self.assertIsInstance(serializer.data['project_idea_comments'], list)

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

        self.assertTrue(serializer.is_valid(), serializer.errors)
        # check the internal value "validated_data"
        self.assertEqual(serializer.validated_data['title'], "Spaced Title")
        self.assertEqual(serializer.validated_data['description'], "Spaced description")

    def test_profanity_validator_raises_error(self):
        """Verify that the ProfanityValidator blocks profanity, when called from project_idea_serializer"""
        data = {
            "title": "Fuck",
            "description": "description",
            "tags": [self.tag.id],
            "likes": [self.user.id]
        }

        serializer = ProjectIdeaSerializer(data=data)

        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn('title', serializer.errors)
