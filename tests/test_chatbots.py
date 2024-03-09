import unittest
from philo.chatbots import OpenAIChat


class TestOpenAIChat(unittest.TestCase):
    def setUp(self):
        self.chatbot = OpenAIChat(model="gpt-3.5-turbo")
        return super().__init__()

    def test_send_receive(self):
        self.chatbot.send_receive("Hello")
        # Check that the first message is from the system
        self.assertEqual(self.chatbot.messages[0]["role"], "system")
        original_first_message = self.chatbot.messages[0]
        # Check that the second message is from the user and is "Hello"
        self.assertEqual(self.chatbot.messages[1]["role"], "user")
        self.assertEqual(self.chatbot.messages[1]["content"], "Hello")
        # Check that a message was added with role "assistant" and "content" is a string
        self.assertIsInstance(self.chatbot.messages[-1]["content"], str)
        self.assertEqual(self.chatbot.messages[-1]["role"], "assistant")
        # Check that the chatbot can be reset
        self.chatbot.reset_messages()
        # Check that the messages have been reset
        self.assertEqual(self.chatbot.messages, [original_first_message])
