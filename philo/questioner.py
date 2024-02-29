import json
import os
from philo.utils import get_repo_root
from philo.chatbots import OpenAIChat
from philo.prompts import PromptConstructor


class Questioner:

    def __init__(self, fresh_start: bool = False):
        self.history_file_path = os.path.join(get_repo_root(), "history.json")
        self.chatbot = OpenAIChat()
        self.fresh_start = fresh_start
        self.read_history()

    def read_history(self):
        try:
            if self.fresh_start:
                # Delete the history file
                os.remove(self.history_file_path)
            with open(self.history_file_path, "r") as f:
                self.history = json.load(f)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            if not os.path.exists(self.history_file_path):
                with open(self.history_file_path, "w") as f:
                    f.write("{}")
            self.history = {}

    def write_history(self):
        with open(self.history_file_path, "w") as f:
            json.dump(self.history, f)

    def get_philosophies(self, prompt_version_number: int):
        pc = PromptConstructor("philosophies")
        prompt = pc.get_prompt(prompt_version_number=prompt_version_number)
        if prompt in self.history:
            return self.history[prompt]
        else:
            out = self.chatbot.send_receive(prompt)
            self.history[prompt] = out
            self.write_history()
            return out

    def get_actions_from_philosophies(
        self,
        prompt_version_number: int,
        philosophy_dict: dict,
    ):
        pc = PromptConstructor("action_from_philosophy")
        prompt = pc.get_prompt(
            user_input=str(philosophy_dict),
            prompt_version_number=prompt_version_number,
        )
        if prompt in self.history:
            return self.history[prompt]
        else:
            out = self.chatbot.send_receive(prompt)
            self.history[prompt] = out
            self.write_history()
            return out
