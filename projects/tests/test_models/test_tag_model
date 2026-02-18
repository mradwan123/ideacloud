from django.test import TestCase
from projects.models import Tag

class TagModelTest(TestCase):
    def test_create_tag(self):
        tag = Tag.objects.create(name="python")
        self.assertEqual(tag.name, "python")
        
    def test_str_method(self):
        tag = Tag.objects.create(name="Django")
        self.assertEqual(str(tag), "Django")    