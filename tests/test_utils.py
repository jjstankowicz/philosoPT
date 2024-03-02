import unittest
from philo.utils import get_prompt, parse_structured_output


class TestUtils(unittest.TestCase):

    def test_get_prompt(self):
        self.prompt = get_prompt("ask_about_philosophies", version_number=0)
        self.assertIsInstance(self.prompt, str, "Prompt is not a string")

    def test_parse_structured_output(self):
        self.text = "[\n {'key': 'This is a test's test'}, \n {'key2': 'This is another's test'}\n]"
        self.list_of_dicts = parse_structured_output(self.text)
        self.assertIsInstance(self.list_of_dicts, list, "List of dicts is not a list")
        self.assertIsInstance(
            self.list_of_dicts[0], dict, "List of dicts does not contain dictionaries"
        )
