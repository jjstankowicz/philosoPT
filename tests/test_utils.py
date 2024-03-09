import unittest
from philo.utils import parse_structured_output, load_history, get_repo_root


class TestUtils(unittest.TestCase):

    def test_parse_structured_output(self):
        self.text = "[\n {'key': 'This is a test's test'}, \n {'key2': 'This is another's test'}\n]"
        self.list_of_dicts = parse_structured_output(self.text)
        self.assertIsInstance(self.list_of_dicts, list, "List of dicts is not a list")
        self.assertIsInstance(
            self.list_of_dicts[0], dict, "List of dicts does not contain dictionaries"
        )

    def test_load_history(self):
        self.history = load_history()
        self.assertIsInstance(self.history, dict, "History is not a dictionary")

    def test_get_repo_root(self):
        rr = get_repo_root()
        self.assertIsInstance(rr, str, "Repo root is not a string")
