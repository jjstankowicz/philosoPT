import json
import os
from tqdm import tqdm
from collections import defaultdict
from typing import Optional, List, Dict
from philo.utils import get_repo_root, parse_structured_output
from philo.chatbots import OpenAIChat
from philo.prompts import PromptConstructor


class Questioner:

    def __init__(self, history_filename_suffix: Optional[str] = "", fresh_start: bool = False):
        history_filename = f"history{history_filename_suffix}.json"
        self.history_file_path = os.path.join(get_repo_root(), history_filename)
        self.set_chatbot()
        self.fresh_start = fresh_start
        self.read_history()

    def set_chatbot(self, model: str = "gpt-4-1106-preview") -> None:
        self.chatbot = OpenAIChat(model=model)

    def log(self, text: str) -> None:
        print(text)

    def log_chatbot(self, text: str, type: str = "") -> None:
        if type not in ["", "prompt", "response"]:
            raise ValueError(f"Invalid type: {type}")
        self.log(f"===== {type} =====")
        self.log("=                =")
        self.log(text)
        self.log("=                =")
        self.log(f"=== End {type} ===")

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

    def send_receive(
        self,
        prompt: str,
        history_key: str,
        force_refresh: bool = False,
        max_retries: int = 15,
    ):
        retries = 0
        while retries < max_retries:
            if force_refresh or (history_key not in self.history):
                try:
                    out = self.chatbot.send_receive(prompt)
                    self.history[history_key] = {"prompt": prompt, "response": out}
                    self.write_history()
                except Exception as e:
                    # Handle specific exceptions or log them
                    retries += 1
                    continue

            else:
                out = self.history[history_key]["response"]

            try:
                parse_structured_output(out)
                return out
            except Exception as e:
                # Log the parsing failure or handle it specifically
                retries += 1
                # Remove the history key to force a refresh
                self.history.pop(history_key, None)

        # After max_retries, either raise an exception or handle the failure case
        raise Exception(f"Failed to parse structured output after {max_retries} attempts.")

    def get_key(self, prompt_name: str, prompt_version_number: int, *args):
        return f"{prompt_name}||{prompt_version_number}||{'||'.join(args)}"

    def get_philosophies(self, prompt_version_number: int, force_refresh: bool = False):
        prompt_name = "philosophies"
        pc = PromptConstructor(prompt_name=prompt_name, prompt_version_number=prompt_version_number)
        prompt = pc.get_prompt()
        history_key = self.get_key(prompt_name, pc.prompt_version_number)
        out = self.send_receive(prompt, history_key, force_refresh)
        return parse_structured_output(out)

    def get_actions_from_philosophies(
        self,
        philosophy_dict: dict,
        prompt_version_number: int,
        force_refresh: bool = False,
    ):
        prompt_name = "action_from_philosophy"
        pc = PromptConstructor(prompt_name=prompt_name, prompt_version_number=prompt_version_number)
        prompt = pc.get_prompt(user_input=str(philosophy_dict))
        history_key = self.get_key(prompt_name, pc.prompt_version_number, philosophy_dict["name"])
        out = self.send_receive(prompt, history_key, force_refresh)
        return parse_structured_output(out)

    def get_clusters_to_actions(
        self,
        prompt_version_number: int,
        action_list: List[str],
        force_refresh: bool = False,
        pbar: bool = False,
        verbose: bool = False,
    ) -> Dict[str, List[Dict[str, str]]]:
        prompt_name = "determine_clusters"
        pc = PromptConstructor(prompt_name=prompt_name, prompt_version_number=prompt_version_number)
        prompt = pc.get_prompt(user_input="\n".join(action_list))
        if verbose:
            self.log_chatbot(prompt, "prompt")
        history_key = self.get_key(prompt_name, pc.prompt_version_number)
        out = self.send_receive(prompt, history_key, force_refresh)
        if verbose:
            self.log_chatbot(out, "response")
        self.cluster_labels = parse_structured_output(out)
        prompt_name = "action_cluster"
        action_cluster_pc = PromptConstructor(
            prompt_name=prompt_name,
            prompt_version_number=prompt_version_number,
        )
        self.collect_action_clusters = []
        iterator = action_list
        if pbar:
            iterator = tqdm(action_list)
        for action in iterator:
            user_input = "{\n\t'action':{{ ACTION }}\n\t'cluster_labels':{{ CLUSTER_LABELS }}\n}"
            user_input = user_input.replace("{{ ACTION }}", action)
            user_input = user_input.replace("{{ CLUSTER_LABELS }}", str(self.cluster_labels))
            prompt = action_cluster_pc.get_prompt(user_input=user_input)
            history_key = self.get_key(prompt_name, pc.prompt_version_number, action)
            out = self.send_receive(prompt, history_key, force_refresh)
            out = parse_structured_output(out)
            out_dict = {"action": action}
            out_dict.update(out)
            self.collect_action_clusters.append(out_dict)
        self.set_cluster_to_actions_dict()
        return dict(self.cluster_to_actions_dict)

    def set_cluster_to_actions_dict(self) -> None:
        collect = defaultdict(list)
        for ac in self.collect_action_clusters:
            action = ac["action"]
            cluster = ac["cluster"]
            reason = ac["reason"]
            aligned = ac["aligned"]
            to_attach = {
                "action": action,
                "reason": reason,
                "aligned": aligned,
            }
            if cluster in collect:
                # Put aligned actions at the beginning of the list
                if aligned:
                    collect[cluster] = [to_attach] + collect[cluster]
                # Put unaligned actions at the end of the list
                else:
                    collect[cluster].append(to_attach)
            else:
                collect[cluster] = [to_attach]
        self.cluster_to_actions_dict = collect

    def get_action_scores(
        self,
        prompt_version_number: int,
        action_list: List[str],
        philosophy_list: List[Dict[str, str]],
        force_refresh: bool = False,
        pbar: bool = False,
        verbose: bool = False,
    ):
        prompt_name = "score_action"
        pc = PromptConstructor(prompt_name=prompt_name, prompt_version_number=prompt_version_number)
        self.collect_action_scores = []
        iterator = action_list
        if pbar:
            iterator = tqdm(action_list)
        for action in iterator:
            user_input = "{\n\t'action':'{{ ACTION }}'\n\t'philosophies':{{ PHILOSOPHIES }}\n}"
            user_input = user_input.replace("{{ ACTION }}", action)
            pl = str(philosophy_list)
            pl = pl.replace("[{'", "[\n\t{'")
            pl = pl.replace("'}, {'", "'},\n\t{'")
            pl = pl.replace("'}]", "'}\n\t\t]")
            user_input = user_input.replace("{{ PHILOSOPHIES }}", pl)
            prompt = pc.get_prompt(user_input=user_input)
            if verbose:
                self.log_chatbot(prompt, "prompt")
            history_key = self.get_key(prompt_name, pc.prompt_version_number, action)
            out = self.send_receive(prompt, history_key, force_refresh)
            if verbose:
                self.log_chatbot(out, "response")
            for d in parse_structured_output(out):
                d_out = {"action": action}
                d_out.update(d)
                self.collect_action_scores.append(d_out)
        return self.collect_action_scores
