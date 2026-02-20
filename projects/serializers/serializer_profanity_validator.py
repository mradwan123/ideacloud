import json
from pathlib import Path
import re
from rest_framework.exceptions import ValidationError

def load_profane_words():
    """Imports a list of banned words from a json file"""
    current_file = Path(__file__).resolve()
    file_path = current_file.parent.parent / 'resources' / 'profanity_words_list.json'

    try:
        with open(file_path, 'r') as f:
            banned_words = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # fallback to an empty list if file is missing or broken
        banned_words = []

    return banned_words


class ProfanityValidator:
    """
    Makes sure that there are no curse or swearwords etc in the titles or text bodies.
    For the sake of simplicity, there are no advanced checks to prevent false positives
    and we only cover the english language.
    """
    def __init__(self):
        self.profane_words = load_profane_words()

    def __call__(self, value):
        # DEBUG: See what is actually being loaded
        print(f"Checking against: {self.profane_words}")
        for word in self.profane_words:
            # the /b ensures that we only check for full words, not contained inside a word (like 'Tit' in 'Title')
            # re.escape() ensures that special characters are escaped
            pattern = rf'\b{re.escape(word)}\b'

            # IGNORECASE replaces the former word().lower comparison
            if re.search(pattern, value, re.IGNORECASE):
                raise ValidationError(f'The word "{word}" is not allowed (profanity filter).')