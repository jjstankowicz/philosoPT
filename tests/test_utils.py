import unittest
from philo.utils import get_prompt

class TestGetPrompt(unittest.TestCase):
    def test_get_prompt(self):
        self.prompt = get_prompt("ask_about_philosophies",version_number=0)
        self.assertIsInstance(self.prompt, str, "Prompt is not a string")