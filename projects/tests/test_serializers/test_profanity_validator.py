from django.test import TestCase
from django.contrib.auth.models import User
from projects.serializers.serializer_profanity_validator import ProfanityValidator, load_profane_words
from rest_framework.exceptions import ValidationError
from unittest.mock import patch

# custom_test_profanity

class ProfanityValidatorTests(TestCase):
    def setUp(self):
        self.validator = ProfanityValidator()

    ### VALID
    def test_valid_text(self):
        """A clean text should not raise an error"""
        # if the line below raises an exception (which it shouldn't), the test automatically fails
        self.validator("This is a harmless text.")

    def test_substring_allowed(self):
        """Ensures that words containing a profane substring are NOT blocked"""
        # 'ass' is in the list but 'assistance' or 'classic' should be allowed
        self.validator("Cassandra needs some assistance.")

    ### INVALID
    def test_case_insensitivity(self):
        """Ensures the filter still catches banned words if they are improperly cased"""
        with self.assertRaises(ValidationError):
            self.validator("Don't be a dIcK.")

    def test_profane_text(self):
        """Ensures that banned words are not passing the validator"""
        text = "Fuck! This is NOT a harmless text!"
        # the 'with' catches the expected error. Otherwise the exception would be thrown prematurely
        with self.assertRaises(ValidationError):
            self.validator(text)

    ### MISC
    def test_profanity_file_load_fallback(self):
        """Force a FileNotFoundError to trigger the fallback"""
        # patch replaces the builtin open function in the load_profane_words call and raises a FileNotFoundError instead
        with patch("builtins.open", side_effect=FileNotFoundError):
            words = load_profane_words()
            self.assertEqual(words, [])
