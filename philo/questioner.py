import json
import os
from tqdm import tqdm
from typing import Optional, List
from philo.utils import get_repo_root, parse_structured_output
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
            json.dump(self.history, f, indent=2)

    def get_philosophies(self, prompt_version_number: int, force_refresh: bool = False):
        prompt_name = "philosophies"
        pc = PromptConstructor(prompt_name)
        prompt = pc.get_prompt(prompt_version_number=prompt_version_number)
        history_key = self.get_key(prompt_name, prompt_version_number)
        out = self.send_recieve(history_key, prompt, force_refresh)
        return parse_structured_output(out)

    def get_actions_from_philosophies(
        self,
        philosophy_dict: dict,
        prompt_version_number: int,
        force_refresh: bool = False,
    ):
        prompt_name = "action_from_philosophy"
        pc = PromptConstructor(prompt_name)
        prompt = pc.get_prompt(
            user_input=str(philosophy_dict),
            prompt_version_number=prompt_version_number,
        )
        history_key = self.get_key(prompt_name, prompt_version_number, philosophy_dict["name"])
        out = self.send_recieve(history_key, prompt, force_refresh)
        return parse_structured_output(out)

    def get_action_clusters(
        self,
        prompt_version_number: int,
        action_list: List[str],
        force_refresh: bool = False,
        pbar: bool = False,
    ):
        prompt_name = "determine_clusters"
        pc = PromptConstructor(prompt_name)
        prompt = pc.get_prompt(
            user_input="\n".join(action_list),
            prompt_version_number=prompt_version_number,
        )
        history_key = self.get_key(prompt_name, prompt_version_number)
        out = self.send_recieve(history_key, prompt, force_refresh)
        self.cluster_labels = parse_structured_output(out)
        prompt_name = "action_cluster"
        action_cluster_pc = PromptConstructor(prompt_name)
        collect_actions = []
        iterator = action_list
        if pbar:
            iterator = tqdm(action_list)
        for action in iterator:
            user_input = "{\n\t'action':{{ ACTION }}\n\t'cluster_labels':{{ CLUSTER_LABELS }}\n}"
            user_input = user_input.replace("{{ ACTION }}", action)
            user_input = user_input.replace("{{ CLUSTER_LABELS }}", str(self.cluster_labels))
            prompt = action_cluster_pc.get_prompt(
                user_input=user_input,
                prompt_version_number=prompt_version_number,
            )
            history_key = self.get_key(prompt_name, prompt_version_number, action)
            out = self.send_recieve(history_key, prompt, force_refresh)
            out = parse_structured_output(out)
            out_dict = {"action": action}
            out_dict.update(out)
            collect_actions.append(out_dict)
        return collect_actions

    def send_recieve(self, history_key: str, prompt: str, force_refresh: bool = False):
        if force_refresh or (history_key not in self.history):
            out = self.chatbot.send_receive(prompt)
            self.history[history_key] = {"prompt": prompt, "response": out}
            self.write_history()
        else:
            out = self.history[history_key]["response"]
        return out

    def get_key(self, prompt_name: str, prompt_version_number: int, *args):
        return f"{prompt_name}||{prompt_version_number}||{'_'.join(args)}"
