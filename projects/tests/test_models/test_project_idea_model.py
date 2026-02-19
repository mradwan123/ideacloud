from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from projects.models import ProjectIdea, Tag
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class ProjectIdeaModelTests(TestCase):
    def setUp(self):
        # create test user
        self.user = User.objects.create_user(username="author", password="password")
        # create test project_idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test Idea",
            author=self.user,
            description="Descriptive text",
        )

    ### VALID
    def test_create_project_idea(self):
        """Verify, that the project_idea gets created correctly and without error"""
        self.assertEqual(self.project_idea.title, "Test Idea")
        self.assertEqual(self.project_idea.description, "Descriptive text")
        self.assertEqual(self.project_idea.author.username, self.user.username)

    def test_created_on_correct_timestamp(self):
        """Verify that timestamps are generated correctly"""
        self.assertIsNotNone(self.project_idea.created_on)
        now = timezone.now()
        # we use AlmostEqual, because we can't compare accurately on a detailed level because the code takes time to run
        self.assertAlmostEqual(
            self.project_idea.created_on,
            now,
            delta=timedelta(minutes=1)
        )

    def test_project_idea_str_method(self):
        """Verify the correctness of the string returned by the __str__ method"""
        # we don't test for the timestamp here. If the rest works, so should the timestamp and we would
        # have similar problems comparing as in the timestamp test itself
        self.assertIn(
            f"Project: 'Test Idea' Submitted by: '{self.user.username}'",
            str(self.project_idea))

    def test_project_idea_str_method_deleted_user(self):
        """Verify that the __str__ method replaces the username of a deleted user correctly with 'Deleted User'"""
        # we don't test for the timestamp here. If the rest works, so should the timestamp and we would
        # have similar problems comparing as in the timestamp test itself
        self.user.delete()

        # sync the object in memory with the database state (python object isn't updated after we delete from db)
        self.project_idea.refresh_from_db()

        self.assertIn(
            "Project: 'Test Idea' Submitted by: 'Deleted User'",
            str(self.project_idea))

    def test_project_idea_updates_correctly_after_user_deletion(self):
        """Verify that the author is deleted after user deletion but the ProjectIdea remains in db"""
        self.user.delete()
        # refresh the idea instance from the database
        self.project_idea.refresh_from_db()

        # author should now be NULL
        self.assertIsNone(self.project_idea.author)
        self.assertTrue(ProjectIdea.objects.filter(id=self.project_idea.id).exists())

    ### INVALID
    def test_create_project_idea_title_too_long(self):
        """Ensure that a title exceeding max_length raises a ValidationError"""
        # we're using the ProjectIdea constructor instead of .objects.create, so we don't attempt to write
        # directly into the database, which can lead to problems in eg. SQLite
        project_idea = ProjectIdea(
            title="A" * 201,
            author=self.user,
            description="Descriptive text",
        )
        with self.assertRaises(ValidationError):
            # this triggers model constraint checks
            project_idea.full_clean()


class ProjectIdeaModelTagTests(TestCase):
    def setUp(self):
        self.tag_python = Tag.objects.create(name="python")
        self.tag_automation = Tag.objects.create(name="automation")
        self.project = ProjectIdea.objects.create(
            title="A python powered automation tool",
            description="Automates mundane tasks with a python script"
        )

    ### VALID
    def test_add_tags_to_project(self):
        """Ensures that multiple tags can be added to a project"""
        self.project.tags.add(self.tag_python, self.tag_automation)

        self.assertEqual(self.project.tags.count(), 2)
        self.assertIn(self.tag_python, self.project.tags.all())
        self.assertIn(self.tag_automation, self.project.tags.all())

    def test_remove_tag_from_project(self):
        """Ensures that a tag can be removed from a project and others persist"""
        self.project.tags.add(self.tag_python, self.tag_automation)

        self.project.tags.remove(self.tag_automation)

        self.assertEqual(self.project.tags.count(), 1)
        self.assertIn(self.tag_python, self.project.tags.all())
        self.assertNotIn(self.tag_automation, self.project.tags.all())

        # ensure the Tag object still exists in the db
        self.assertTrue(Tag.objects.filter(name="automation").exists())


class ProjectIdeaModelLikesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="password")
        self.project = ProjectIdea.objects.create(
            title="Universally liked project",
            description="Everybody loves this!"
        )

    def test_user_likes_project(self):
        """Ensure that adding a User to the likes works and increases the counter"""
        self.project.likes.add(self.user)

        self.assertEqual(self.project.likes.count(), 1)
        self.assertIn(self.user, self.project.likes.all())

    def test_user_likes_project_twice(self):
        """
        Checks that liking a post twice doesn't do anything
        (Frontend should handle that but desync can do all sorts of stuff)
        """
        self.project.likes.add(self.user)
        self.project.likes.add(self.user)
        self.assertEqual(self.project.likes.count(), 1)
