from django.test import TestCase
from django.core.exceptions import ValidationError
from projects.serializers.serializer_project_group_serializer import ProjectGroupSerializer
from projects.models import ProjectIdea, ProjectGroup
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


class TestProjectGroupSerializer(TestCase):

    def setUp(self):
        User = get_user_model()
        self.group_name = "test_group"
        self.group_description = "test description"
        self.password = "TestPassword1,"
        self.user = User.objects.create_user(username="test_user",
                                             password=self.password)
        self.user2 = User.objects.create_user(username="test_user2",
                                              password=self.password)
        self.project_idea = ProjectIdea.objects.create(title="test idea",
                                                       author=self.user,
                                                       description="test description",)
        self.project_group_data = {"name": "test group",
                                   "description": "test description",
                                   "project_idea": self.project_idea.id,
                                   "owner": self.user.id}
        self.request = type('Request', (), {'user': self.user})()
        
    def test_serializer_project_group_valid(self):
        serializer = ProjectGroupSerializer(data=self.project_group_data)
        serializer.context['request'] = self.request
        self.assertTrue(serializer.is_valid())

        project_group = serializer.save()
        self.assertEqual(project_group.name, self.project_group_data.get("name"))
        self.assertEqual(project_group.description, self.project_group_data.get("description"))
        self.assertEqual(project_group.project_idea, self.project_idea)
        self.assertEqual(project_group.owner, self.user)
        #print(project_group.created_at, timezone.now())
        self.assertAlmostEqual(project_group.created_on, timezone.now(), delta=timedelta(minutes=1))

    def test_serializer_project_group_name_missing(self):
        del self.project_group_data["name"]
        serializer = ProjectGroupSerializer(data=self.project_group_data)
        serializer.context['request'] = self.request
        self.assertFalse(serializer.is_valid())

    def test_serializer_project_group_description_missing(self):
        del self.project_group_data["description"]
        serializer = ProjectGroupSerializer(data=self.project_group_data)
        serializer.context['request'] = self.request
        self.assertFalse(serializer.is_valid())

    def test_serializer_project_group_name_duplicate(self):
        serializer1 = ProjectGroupSerializer(data=self.project_group_data)
        serializer1.context['request'] = self.request
        self.assertTrue(serializer1.is_valid())
        serializer1.save()

        serializer2 = ProjectGroupSerializer(data=self.project_group_data)
        serializer2.context['request'] = self.request
        self.assertFalse(serializer2.is_valid())

    def test_serializer_project_group_to_reprentation(self):
        project_group = ProjectGroup.objects.create(name="group name",
                                                    description="some description",
                                                    project_idea=self.project_idea,
                                                    owner=self.user)
        project_group.members.add(self.user)
        project_group.members.add(self.user2)
        serializer = ProjectGroupSerializer()
        representation_value = serializer.to_representation(project_group)
        self.assertEqual(representation_value["owner"]["id"], self.user.id)
        self.assertEqual(representation_value["owner"]["username"], self.user.username)
        self.assertEqual(len(representation_value["members"]), 2)
        members = representation_value["members"]
        member_ids = [member.get("id") for member in members]
        member_usernames = [member.get("username") for member in members]
        self.assertIn(self.user.id, member_ids)
        self.assertIn(self.user2.id, member_ids)
        self.assertIn(self.user.username, member_usernames)
        self.assertIn(self.user2.username, member_usernames)



