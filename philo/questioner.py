import json
import os
from philo.utils import get_prompt
from philo.chatbots import OpenAI


class Questioner:
    def __init__(self, fresh_start: bool = False):
        self.chatbot = OpenAI()
        self.fresh_start = fresh_start
        self.read_history()

    def read_history(self):
        try:
            with open("history.json", "r") as f:
                self.history = json.load(f)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            if not os.path.exists("history.json"):
                with open("history.json", "w") as f:
                    f.write("{}")
            self.history = {}

    def write_history(self):
        with open("history.json", "w") as f:
            json.dump(self.history, f)

    def get_philosophies(self, version_number: int):
        prompt = get_prompt("ask_about_philosophies", version_number=version_number)
        if prompt in self.history:
            return self.history[prompt]
        else:
            out = self.chatbot.send_receive(prompt)
            self.history[prompt] = out
            self.sync_history()
            return out