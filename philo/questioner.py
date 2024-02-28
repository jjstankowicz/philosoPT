import json
import os
from philo.utils import get_prompt, get_repo_root
from philo.chatbots import OpenAIChat


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

    def get_philosophies(self, version_number: int):
        prompt = get_prompt("ask_about_philosophies",
                            version_number=version_number)
        if prompt in self.history:
            return self.history[prompt]
        else:
            out = self.chatbot.send_receive(prompt)
            self.history[prompt] = out
            self.write_history()
            return out

    def get_actions_from_philosophies(
        self,
        version_number: int,
        philosophy_dict: dict,
    ):
        prompt = get_prompt("ask_about_action_from_philosophy",
                            version_number=version_number)
        prompt.replace("{{ USER_INPUT }}", str(philosophy_dict))
        if prompt in self.history:
            return self.history[prompt]
        else:
            out = self.chatbot.send_receive(prompt)
            self.history[prompt] = out
            self.write_history()
            return out
