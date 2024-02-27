import unittest
import json
from philo.chatbots import OpenAIChat
from philo.utils import get_prompt

class TestPrompts(unittest.TestCase):
    def setUp(self):
        self.chatbot = OpenAIChat()
        self.prompts = {}
        prompt_titles = ["ask_about_philosophies"]
        for prompt_title in prompt_titles:
            self.prompts[prompt_title] = get_prompt("ask_about_philosophies",version_number=-1)
        return super().__init__()

    def test_ask_about_philosophies(self):
        out = self.chatbot.send_receive(self.prompts["ask_about_philosophies"])
        self.assertIsInstance(out, str, "Response is not a string")
        # Test if out can be converted to a list of dictionaries
        try:
            out = json.loads(out)
            self.assertIsInstance(out, list, "Response is not a list")
            self.assertIsInstance(out[0], dict, "Response is not a list of dictionaries")
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")