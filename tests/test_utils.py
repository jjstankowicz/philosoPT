import unittest
from philo.utils import get_prompt, text_to_list_of_dicts


class TestUtils(unittest.TestCase):

    def test_get_prompt(self):
        self.prompt = get_prompt("ask_about_philosophies", version_number=0)
        self.assertIsInstance(self.prompt, str, "Prompt is not a string")

    def test_text_to_list_of_dicts(self):
        self.text = "[\n {'key': 'This is a test's test'}, \n {'key2': 'This is another's test'}\n]"
        self.list_of_dicts = text_to_list_of_dicts(self.text)
        self.assertIsInstance(self.list_of_dicts, list,
                              "List of dicts is not a list")
        self.assertIsInstance(self.list_of_dicts[0], dict,
                              "List of dicts does not contain dictionaries")
