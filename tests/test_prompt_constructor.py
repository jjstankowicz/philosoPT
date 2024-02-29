import unittest
from philo.chatbots import OpenAIChat
from philo.utils import text_to_list_of_dicts
from philo.prompts import PromptConstructor


class TestPromptConstructor(unittest.TestCase):

    def setUp(self):
        self.chatbot = OpenAIChat()
        self.prompts = {}
        self.prompt_titles = ["philosophies", "action_from_philosophy"]
        return super().__init__()

    def test_non_existent_prompt(self):
        # Verify that a ValueError is raised
        # when a non-existent prompt is passed to PromptConstructor
        with self.assertRaises(ValueError):
            PromptConstructor("non_existent_prompt")

    def test_set_prompt_parts(self):
        # Verify that the prompt parts are set correctly
        for title in self.prompt_titles:
            pc = PromptConstructor(title)
            pc.set_prompt_parts()
            self.assertIsInstance(pc.prompt_parts, dict)

    def test_get_prompt(self):
        # Verify that the prompt is returned correctly
        for title in self.prompt_titles:
            pc = PromptConstructor(title)
            test_user_input = "SOME TEST STRING"
            prompt = pc.get_prompt(test_user_input, prompt_version_number=0)
            self.assertIsInstance(prompt, str, "Prompt is not a string.")
            # Only test for user input if it is in the prompt
            if "user_input" in pc.prompt_parts:
                self.assertIn(test_user_input, prompt, "User input not found in prompt.")
