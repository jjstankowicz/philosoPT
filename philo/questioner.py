import json
import os
from typing import Optional
from philo.utils import get_repo_root
from philo.chatbots import OpenAIChat
from philo.prompts import PromptConstructor


class Questioner:

    def __init__(self, history_filename_suffix: Optional[str] = "", fresh_start: bool = False):
        history_filename = f"history{history_filename_suffix}.json"
        self.history_file_path = os.path.join(get_repo_root(), history_filename)
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
        philosophy_dict: dict,
        prompt_version_number: int,
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
