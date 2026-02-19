from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from projects.models import ProjectIdea, ProjectIdeaComment, Tag
from django.utils import timezone
from datetime import timedelta
class ProjectIdeaCommentTesting(TestCase):
    """
    Test comments on project idea. First setup user and project idea. Then comment testing.
    """
    def setUp(self):
        User = get_user_model()
        # create test user
        self.user = User.objects.create_user(username="author", password="password")
        
        # create test project_idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test Idea",
            author=self.user,
            description="Descriptive text",
        )
        
        #creaate project_idea_comment
        self.project_idea_comment = ProjectIdeaComment(
            user = self.user,
            project_idea = self.project_idea,
            content = 'Testing Project Idea Comment.',
        )
        
#----- VALID TEST --------------

    def test_create_project_idea(self):
        """Verify, that the project_idea_comments gets created correctly and without error"""
        self.assertEqual(self.project_idea_comment.content, "Testing Project Idea Comment.")
        
    def test_created_on_correct_timestamp(self):
        """Verify that timestamps are generated correctly"""
        self.assertIsNotNone(self.project_idea_comment.created_on)
        now = timezone.now()
        # we use AlmostEqual, because we can't compare accurately on a detailed level because the code takes time to run
        self.assertAlmostEqual(
            self.project_idea_comment.created_on,
            now,
            delta=timedelta(minutes=1)
        )
        
    def test_project_idea_comment_str_method(self):
        """Verify the correctness of the string returned by the __str__ method"""
        # we don't test for the timestamp here. If the rest works, so should the timestamp and we would
        # have similar problems comparing as in the timestamp test itself
        self.assertIn(
            f"'Test Idea' Submitted by: '{self.user.username}'",
            str(self.project_idea_comment))
        
    ### INVALID
    def test_create_project_idea_comment_too_long(self):
        """Ensure that a title exceeding max_length raises a ValidationError"""
        # we're using the ProjectIdeaComment constructor instead of .objects.create, so we don't attempt to write
        # directly into the database, which can lead to problems in eg. SQLite
        project_idea_comment = ProjectIdeaComment(
            content="A" * 501,
        )
        with self.assertRaises(ValidationError):
            # this triggers model constraint checks
            project_idea_comment.full_clean()
