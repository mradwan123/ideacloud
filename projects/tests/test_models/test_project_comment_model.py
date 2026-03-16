from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from projects.models import ProjectIdea, ProjectGroup, FinishedProject, ProjectComment

User = get_user_model()


class ProjectCommentModelTests(TestCase):
    def setUp(self):
        # create user
        self.user_author = User.objects.create_user(username="author", password="password")

        # create a project idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test Idea",
            author=self.user_author,
            description="Descriptive text",
        )

        # create a finished project (requires a group first)
        self.project_group = ProjectGroup.objects.create(
            name="Test Group",
            description="Group description",
            project_idea=self.project_idea,
            owner=self.user_author
        )
        self.finished_project = FinishedProject.objects.create(
            title="Finished App",
            description="Done!",
            project_group=self.project_group
        )

        # create comments
        self.comment_on_idea = ProjectComment(
            author=self.user_author,
            project_idea=self.project_idea,
            content="Testing Project Idea Comment"
        )

        self.comment_on_finished = ProjectComment(
            author=self.user_author,
            finished_project=self.finished_project,
            content="Testing Finished Project Comment"
        )

    ### VALID
    ## CREATE
    def test_create_project_comment_on_idea(self):
        """Verify that the comment on a project idea gets created correctly and without error"""
        self.assertEqual(self.comment_on_idea.content, "Testing Project Idea Comment")
        self.assertEqual(self.comment_on_idea.author, self.user_author)

    def test_create_project_comment_on_finished_project(self):
        """Verify that the comment on a finished project gets created correctly and without error"""
        self.assertEqual(self.comment_on_finished.content, "Testing Finished Project Comment")
        self.assertEqual(self.comment_on_finished.author, self.user_author)

    def test_created_on_correct_timestamp(self):
        """Verify that timestamps are generated correctly upon saving"""
        self.comment_on_idea.save()
        self.assertIsNotNone(self.comment_on_idea.created_on)

        now = timezone.now()
        # we use AlmostEqual because we can't compare accurately on a detailed level due to runtime delay
        self.assertAlmostEqual(
            self.comment_on_idea.created_on,
            now,
            delta=timedelta(minutes=1)
        )

    # STR
    def test_project_comment_str_method(self):
        """Verify the correctness of the string returned by the __str__ method"""
        expected_idea_str = f"Comment by {self.user_author.username} on {self.project_idea}"
        self.assertEqual(str(self.comment_on_idea), expected_idea_str)

    ### INVALID
    ## VALIDATION
    def test_create_project_comment_too_long(self):
        """Ensure that a comment exceeding max_length raises a ValidationError"""
        long_comment = ProjectComment(
            author=self.user_author,
            project_idea=self.project_idea,
            content="A" * 501,
        )
        with self.assertRaises(ValidationError):
            # triggers model constraint and length checks
            long_comment.full_clean()

    def test_constraint_fails_if_both_idea_and_finished_project_attached(self):
        """Ensures the CheckConstraint prevents a comment from being attached to both models simultaneously"""
        invalid_comment = ProjectComment(
            author=self.user_author,
            project_idea=self.project_idea,
            finished_project=self.finished_project,
            content="This should fail"
        )
        with self.assertRaises(ValidationError):
            invalid_comment.full_clean()

    def test_constraint_fails_if_no_project_attached(self):
        """Ensures the CheckConstraint prevents a comment from being saved with no attached project"""
        invalid_comment = ProjectComment(
            author=self.user_author,
            content="This should fail too"
        )
        with self.assertRaises(ValidationError):
            invalid_comment.full_clean()
