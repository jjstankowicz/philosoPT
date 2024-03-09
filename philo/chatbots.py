from openai import OpenAI
from philo.utils import MessageType


class OpenAIChat:
    def __init__(
        self,
        model: str = "gpt-4-1106-preview",
        role_str: str = "You are a helpful assistant.",
    ) -> None:
        self.client = OpenAI()
        self.role_str = role_str
        if model not in ["gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo"]:
            raise ValueError(f"Model {model} not available for chat.")
        self.model = model
        self.current_answer = ""
        self.current_question = ""
        self.reset_messages()

    def reset_messages(self) -> None:
        """Reset the chat history to the initial state."""
        self.messages = [{"role": "system", "content": self.role_str}]

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat history

        Args:
            role (str): The role of the speaker
            content (str): The content of the message
        """
        self.messages.append({"role": role, "content": content})

    def get_response(self, temperature: float = 0.0, seed: int = 1) -> str:
        """Get a response from the chatbot

        Args:
            temperature (float, optional): The randomness of the response. Higher values are more random. Defaults to 0.0.
            seed (int, optional): A seed for the randomness. Defaults to 1.

        Returns:
            str: The response from the chatbot
        """
        # For every message in the chat history, keep only the role and content
        messages = [
            {"role": message["role"], "content": message["content"]} for message in self.messages
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            seed=1,
        )
        return response

    def set_messages_from(self, messages: MessageType) -> None:
        """Set the chat history from a list of messages

        Args:
            messages (MessageType): The list of messages to use as the chat history
        """
        self.messages = messages

    def get_messages(self) -> MessageType:
        """Get the chat history

        Returns:
            MessageType: The chat history
        """
        return self.messages

    def send_receive(self, user_question: str, temperature: float = 0.0, seed: int = 1) -> str:
        """Send and receive a message from the chatbot

        Args:
            user_question (str): The message to send to the chatbot.
            temperature (float, optional): The randomness of the response. Higher values are more random. Defaults to 0.0.
            seed (int, optional): The seed for the randomness. Defaults to 1.

        Returns:
            str: _description_
        """
        self.current_question = user_question
        self.add_message("user", user_question)
        response = self.get_response(temperature=temperature, seed=seed)
        response = response.choices[0].message.content
        self.add_message("assistant", response)
        self.current_answer = response
        return response
