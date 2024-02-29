import unittest
from philo.chatbots import OpenAIChat
from philo.utils import text_to_list_of_dicts
from philo.prompt_constructor import PromptConstructor


class TestPrompts(unittest.TestCase):

    def setUp(self):
        self.chatbot = OpenAIChat()
        self.prompts = {}
        self.prompt_titles = ["philosophies", "action_from_philosophy"]
        return super().__init__()

    def test_non_existent_prompt(self):
        self.
