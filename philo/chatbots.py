from typing import Generator
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
        self.messages = [{"role": "system", "content": self.role_str}]

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def get_response(self, temperature: float = 0.0, seed: int = 1) -> str:
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

    def stream_response(self) -> Generator[str, None, None]:
        messages = [
            {"role": message["role"], "content": message["content"]} for message in self.messages
        ]
        for response in self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        ):
            partial_response = response.choices[0].delta.content or ""
            yield partial_response

    def set_messages_from(self, messages: MessageType) -> None:
        self.messages = messages

    def get_messages(self) -> MessageType:
        return self.messages

    def send_receive(self, user_question: str, temperature: float = 0.0, seed: int = 1) -> str:
        self.current_question = user_question
        self.add_message("user", user_question)
        response = self.get_response(temperature=temperature, seed=seed)
        response = response.choices[0].message.content
        self.add_message("assistant", response)
        self.current_answer = response
        return response
