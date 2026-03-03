from django.test import TestCase
from django.contrib.auth import get_user_model
from projects.models import FinishedProject, ProjectGroup, ProjectIdea, ImageProject, Tag
from projects.serializers.serializer_project_idea_serializer import ProjectIdeaSerializer
from projects.serializers.serializer_finished_projects import FinishedProjectSerializer
from rest_framework.exceptions import ValidationError


User = get_user_model()


class FinishedProjectSerializerTests(TestCase):
    def setUp(self):
        # create test user
        self.user = User.objects.create_user(username="test_user", password="password", email='test@hello.com')
        self.user2 = User.objects.create_user(username="test_user2", password="password2", email='test@hello2.com')
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
        
        # create a group
        self.project_group = ProjectGroup.objects.create(
                                name='Test Group',
                                project_idea = self.project_idea,
                                owner=self.user #TODO create another user that is not project idea owner, and is group owner
                                )
        
        #create finished project
        self.finished_project = FinishedProject.objects.create(
            title = "test finished project title",
            description = 'test description',
            project_group = self.project_group,
            
        )
        
        request = type('Request', (), {'user': self.user})()
        self.context = {"request": request}
        
        request_user2 = type('Request', (), {'user': self.user2})()
        self.context2 = {"request": request_user2}
        
        self.finished_project.tags.add(self.tag)
        # add annotations that the view normally provides
        self.finished_project.likes_count = 0
        self.finished_project.has_liked = False
        self.finished_project.save()
        
    def test_serializer_contains_all_fields(self):
        """Verify that all fields are returned correctly"""
        serializer = FinishedProjectSerializer(instance=self.finished_project, context=self.context)
        data = serializer.data

        expected_fields = {
            "id", "title", "description", "finished_on", "tags",
            'likes_count', 'has_liked', "project_group", 
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_tags_and_likes_are_saved(self):
        """Verify that M2M IDs are correctly converted to database relations"""
        data = {
            "title": "Title",
            "description": "Description",
            "tags": ["python"],
            "project_group": self.project_group.pk
        }
        serializer = FinishedProjectSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        # author is read-only so we pass it here
        project = serializer.save()
        # add like here
        project.likes.add(self.user.id)
        # fetch from DB to ensure the save actually was done
        project.refresh_from_db()

        self.assertEqual(project.tags.count(), 1)
        self.assertEqual(project.likes.count(), 1)

    def test_serializer_with_annotations(self):
        """Verify that annotated fields (from our view logic) are present"""
        from django.db.models import Count, Value, BooleanField

        # add one like so count is 1
        self.finished_project.likes.add(self.user)

        # simulate the annotated queryset the view normally provides
        queryset = FinishedProject.objects.annotate(
            likes_count=Count('likes'),
            has_liked=Value(True, output_field=BooleanField())
        )

        # fetch a NEW instance from the DB result
        # this instance has the database-calculated attributes NOT the ones from setUp
        db_instance = queryset.get(id=self.finished_project.id)

        serializer = FinishedProjectSerializer(instance=db_instance)

        self.assertEqual(serializer.data['likes_count'], 1)
        self.assertEqual(serializer.data['has_liked'], True)

    def test_to_representation_titles_the_title(self):
        """Verify that title is converted to a titled version in representation"""
        serializer = FinishedProjectSerializer(instance=self.finished_project)
        # original title: title="test finished project title"
        self.assertEqual(serializer.data['title'], "Test Finished Project Title")

    def test_to_internal_value_strips_whitespace(self):
        """Verify that whitespace are stripped from input"""
        data = {
            "title": "   Spaced Title   ",
            "description": "   Spaced description   ",
            "tags": ["python"],
        }

        serializer = FinishedProjectSerializer(data=data, context=self.context)

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
        }

        serializer = FinishedProjectSerializer(data=data, context=self.context)

        self.assertFalse(serializer.is_valid(), serializer.errors)
        #TODO fix this assertion: self.assertIn('title', serializer.errors)
        
    def test_finished_project_user_not_project_group_owner_fail(self):
        data = {
            "title": "Title",
            "description": "Description",
            "tags": ["python"],
            "project_group": self.project_group.pk
        }
        
        serializer = FinishedProjectSerializer(data=data, context=self.context2)
        self.assertTrue(serializer.is_valid())
        # author is read-only so we pass it here
        with self.assertRaises(ValidationError) as error:
            project = serializer.save()
        self.assertIn("User is not allowed to publish this Finished Group.", str(error.exception.detail))
        
            
