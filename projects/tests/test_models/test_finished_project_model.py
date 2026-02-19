from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from projects.models import ProjectIdea, ProjectGroup, FinishedProject, Tag
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class FinishedProjectModelTests(TestCase):
    def setUp(self):
        # create test user
        self.user = User.objects.create_user(username="owner", password="password")
        # create test project_idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test idea",
            author=self.user,
            description="Descriptive text",
        )
        # create test group
        self.project_group = ProjectGroup.objects.create(
            name="Test group",
            project_idea=self.project_idea,
            owner=self.user
        )
        # create test finished_project
        self.finished_project = FinishedProject.objects.create(
            title="Test finished project",
            description="Descriptive text",
            project_group=self.project_group
        )

    ### VALID
    def test_create_finished_project(self):
        """Verify, that the FinishedProject gets created correctly and without error"""
        self.assertEqual(self.finished_project.title, "Test finished project")
        self.assertEqual(self.finished_project.description, "Descriptive text")
        self.assertEqual(self.finished_project.project_group, self.project_group)

    def test_finished_on_correct_timestamp(self):
        """Verify that timestamps are generated correctly"""
        self.assertIsNotNone(self.finished_project.finished_on)
        now = timezone.now()
        # we use AlmostEqual, because we can't compare accurately on a detailed level because the code takes time to run
        self.assertAlmostEqual(
            self.finished_project.finished_on,
            now,
            delta=timedelta(minutes=1)
        )

    def test_finished_project_str_method(self):
        """Verify the correctness of the string returned by the __str__ method"""
        # we don't test for the timestamp here. If the rest works, so should the timestamp and we would
        # have similar problems comparing as in the timestamp test itself
        self.assertIn(
            f"Project: 'Test finished project' Submitted by: '{self.project_group.name}'",
            str(self.finished_project)
        )

    def test_finished_project_str_method_deleted_group(self):
        """Verify that the __str__ method replaces the group name of a deleted group correctly with 'Deleted Group'"""
        self.project_group.delete()

        # refresh the project instance from the database
        self.finished_project.refresh_from_db()

        self.assertIn(
            "Project: 'Test finished project' Submitted by: 'Deleted Group'",
            str(self.finished_project))

    def test_finished_project_updates_correctly_after_group_deletion(self):
        """Verify that the group is deleted after group deletion but the FinishedProject remains in db"""
        self.project_group.delete()
        # refresh the Project instance from the database
        self.finished_project.refresh_from_db()

        # group should now be NULL
        self.assertIsNone(self.finished_project.project_group)
        # project should still exist
        self.assertTrue(FinishedProject.objects.filter(id=self.finished_project.id).exists())

    ### INVALID
    def test_create_finished_project_title_too_long(self):
        """Ensure that a title exceeding max_length raises a ValidationError"""
        # we're using the FinishedProject constructor instead of .objects.create, so we don't attempt to write
        # directly into the database, which can lead to problems in eg. SQLite
        finished_project = FinishedProject(
            title="A" * 201,
            project_group=self.project_group,
            description="Descriptive text",
        )
        with self.assertRaises(ValidationError):
            # this triggers model constraint checks
            finished_project.full_clean()


class FinishedProjectModelTagTests(TestCase):
    def setUp(self):
        # create test user
        self.user = User.objects.create_user(username="owner", password="password")
        # create test project_idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test idea",
            author=self.user,
            description="Descriptive text",
        )
        # create test group
        self.project_group = ProjectGroup.objects.create(
            name="Test group",
            project_idea=self.project_idea,
            owner=self.user
        )
        # create test tags
        self.tag_python = Tag.objects.create(name="python")
        self.tag_automation = Tag.objects.create(name="automation")
        # create test finished project
        self.finished_project = FinishedProject.objects.create(
            title="A python powered automation tool",
            project_group=self.project_group,
            description="Automates mundane tasks with a python script",
        )

    ### VALID
    def test_add_tags_to_finished_project(self):
        """Ensures that multiple tags can be added to a finished project"""
        self.finished_project.tags.add(self.tag_python, self.tag_automation)

        self.assertEqual(self.finished_project.tags.count(), 2)
        self.assertIn(self.tag_python, self.finished_project.tags.all())
        self.assertIn(self.tag_automation, self.finished_project.tags.all())

    def test_remove_tag_from_finished_project(self):
        """Ensures that a tag can be removed from a finished project and others persist"""
        self.finished_project.tags.add(self.tag_python, self.tag_automation)

        self.finished_project.tags.remove(self.tag_automation)

        self.assertEqual(self.finished_project.tags.count(), 1)
        self.assertIn(self.tag_python, self.finished_project.tags.all())
        self.assertNotIn(self.tag_automation, self.finished_project.tags.all())

        # ensure the Tag object still exists in the db
        self.assertTrue(Tag.objects.filter(name="automation").exists())


class FinishedProjectModelLikesTests(TestCase):
    def setUp(self):
        # create test user
        self.user = User.objects.create_user(username="owner", password="password")
        # create test project_idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test idea",
            author=self.user,
            description="Descriptive text",
        )
        # create test group
        self.project_group = ProjectGroup.objects.create(
            name="Test group",
            project_idea=self.project_idea,
            owner=self.user
        )
        # create test finished project
        self.finished_project = FinishedProject.objects.create(
            title="A python powered automation tool",
            project_group=self.project_group,
            description="Automates mundane tasks with a python script",
        )

    def test_user_likes_project(self):
        """Ensure that adding a User to the likes works and increases the counter"""
        self.finished_project.likes.add(self.user)

        self.assertEqual(self.finished_project.likes.count(), 1)
        self.assertIn(self.user, self.finished_project.likes.all())

    def test_user_likes_project_twice(self):
        """
        Checks that liking a post twice doesn't do anything
        (Frontend should handle that but desync can do all sorts of stuff)
        """
        self.finished_project.likes.add(self.user)
        self.finished_project.likes.add(self.user)
        self.assertEqual(self.finished_project.likes.count(), 1)
