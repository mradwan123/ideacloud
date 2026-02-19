from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from projects.models import ProjectGroup, ProjectGroupComment, ProjectIdea
from django.utils import timezone
from datetime import timedelta
class ProjectGroupCommentTesting(TestCase):
    """
    Test comments on project group. First setup user and project group. Then comment testing.
    """
    def setUp(self):
        User = get_user_model()
        # create test user
        self.user = User.objects.create_user(username="author", password="password")

        project_idea = ProjectIdea.objects.create(
            title="Test Idea",
            author=self.user,
            description="Descriptive text",
        )
        
        # create test project_group
        self.project_group = ProjectGroup.objects.create(
            name="Test Group",
            project_idea=project_idea,
            owner=self.user,
            description="Descriptive text",
        )
        
        #creaate project_group_comment
        self.project_group_comment = ProjectGroupComment(author=self.user,
                                                         project_group=self.project_group,
                                                         content='Testing Project Group Comment.')
        
#----- VALID TEST --------------

    def test_create_project_group(self):
        """Verify, that the project_group_comments gets created correctly and without error"""
        self.assertEqual(self.project_group_comment.content, "Testing Project Group Comment.")
        
    def test_created_on_correct_timestamp(self):
        """Verify that timestamps are generated correctly"""
        self.assertIsNotNone(self.project_group_comment.created_on)
        now = timezone.now()
        # we use AlmostEqual, because we can't compare accurately on a detailed level because the code takes time to run
        self.assertAlmostEqual(
            self.project_group_comment.created_on,
            now,
            delta=timedelta(minutes=1)
        )
        
    def test_project_group_comment_str_method(self):
        """Verify the correctness of the string returned by the __str__ method"""
        # we don't test for the timestamp here. If rest works, so should the timestamp and we would
        # have similar problems comparing as in the timestamp test itself
        self.assertIn(
            f"Comment by {self.user.username} on {self.project_group.name}",
            str(self.project_group_comment))
        
    ### INVALID
    def test_create_project_group_comment_too_long(self):
        """Ensure that a title exceeding max_length raises a ValidationError"""
        # we're using the ProjectGroupComment constructor instead of .objects.create, so we don't attempt to write
        # directly into the database, which can lead to problems in eg. SQLite
        project_group_comment = ProjectGroupComment(content="A" * 501)

        with self.assertRaises(ValidationError):
            # this triggers model constraint checks
            project_group_comment.full_clean()
