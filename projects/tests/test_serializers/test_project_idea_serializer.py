from django.contrib.auth import get_user_model
from projects.models import ProjectIdea, ImageProject, ProjectIdeaComment
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

            expected_fields = {'id', 'title', 'author', 'description', 'created_on', 'tags', 'likes', 'images_projects', 'project_idea_comments'}
            self.assertEqual(set(data.keys()), expected_fields)
            
        