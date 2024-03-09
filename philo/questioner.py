import json
import os
from tqdm import tqdm
import time
from collections import defaultdict
from typing import Optional
from philo.utils import get_repo_root, parse_structured_output
from philo.chatbots import OpenAIChat
from philo.prompts import PromptConstructor
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as ol


class Questioner:

    def __init__(self, history_filename_suffix: Optional[str] = "", fresh_start: bool = False):
        history_filename = f"history{history_filename_suffix}.json"
        self.history_file_path = os.path.join(get_repo_root(), history_filename)
        self.set_chatbot()
        self.fresh_start = fresh_start
        self.read_history()

    def set_chatbot(self, model: str = "gpt-4-1106-preview") -> None:
        """Set the chatbot to use for the questioner.

        Args:
            model (str, optional): The model name. Defaults to "gpt-4-1106-preview".
        """
        self.chatbot = OpenAIChat(model=model)

    def log(self, text: str) -> None:
        """Log a message.

        Args:
            text (str): Message to log.
        """
        print(text)

    def log_chatbot(self, text: str, type: str = "") -> None:
        """Pre-formated log for chatbot interactions.

        Args:
            text (str): The text to log.
            type (str, optional): The type ["","prompt","response]. Defaults to "".

        Raises:
            ValueError: Invalid type.
        """
        if type not in ["", "prompt", "response"]:
            raise ValueError(f"Invalid type: {type}")
        self.log(f"===== {type} =====")
        self.log("=                =")
        self.log(text)
        self.log("=                =")
        self.log(f"=== End {type} ===")

    def read_history(self) -> None:
        """Read the history file."""
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

    def write_history(self) -> None:
        """Write the history file."""
        with open(self.history_file_path, "w") as f:
            json.dump(self.history, f, indent=2)

    def send_receive(
        self,
        prompt: str,
        history_key: str,
        force_refresh: bool = False,
        max_retries: int = 15,
    ) -> str:
        """Wrapper to send and receive messages from the chatbot.

        Args:
            prompt (str): The prompt to send to the chatbot.
            history_key (str): The key to use for the history.
            force_refresh (bool, optional): If true, rerun even if history_key is in history. Defaults to False.
            max_retries (int, optional): Maximum number of retries. Defaults to 15.

        Raises:
            Exception: Failed after max_retries attempts.

        Returns:
            str: The response from the chatbot.
        """
        retries = 0
        while retries < max_retries:
            seed = retries + 1
            temperature = retries / max_retries
            try:
                # Check if we need to (re)send the message
                if force_refresh or (history_key not in self.history):
                    self.log("Sending message...")
                    # Send the message and update history
                    out = self.chatbot.send_receive(prompt, seed=seed, temperature=temperature)
                    self.history[history_key] = {"prompt": prompt, "response": out}
                    self.write_history()
                else:
                    # Retrieve response from history if available and no need to force refresh
                    out = self.history[history_key]["response"]

                # Attempt to parse the structured output
                parse_structured_output(out)
                return out  # Return successfully parsed output
            except Exception as e:
                # Handle exceptions (both from sending/receiving and parsing)
                self.log("An error occurred; attempting retry.")
                self.log(f"T={temperature}, seed={seed}")
                self.log(f"Error: {e}")
                retries += 1
                if history_key in self.history:
                    time.sleep(5)  # Give the history time to update
                    del self.history[history_key]  # Remove the history entry to force a refresh
                    self.write_history()
                    time.sleep(5)  # Give the history time to update
                if retries < max_retries:
                    # Optional: modify force_refresh or adjust logic if needed before retrying
                    continue
                else:
                    # Handling case where max retries are reached
                    break  # Break from the loop if max retries have been reached

        # After exhausting max_retries, handle the failure case
        raise Exception(f"Failed after {max_retries} attempts.")

    def get_key(self, prompt_name: str, prompt_version_number: int, *args) -> str:
        """Automatically generate a history key.

        Args:
            prompt_name (str): Name of the prompt.
            prompt_version_number (int): Version number of the prompt.
            *args: Additional arguments to include in the key.

        Returns:
            str: The history key, formatted as "prompt_name||prompt_version_number||args[0]||args[1]||..."
        """
        return f"{prompt_name}||{prompt_version_number}||{'||'.join(args)}"

    def set_philosophies(
        self,
        prompt_version_number: int,
        force_refresh: bool = False,
    ) -> None:
        """Set the philosophies by sending a prompt to the chatbot.

        Args:
            prompt_version_number (int): The version number of the prompt.
            force_refresh (bool, optional): If true, rerun even if history_key is in history. Defaults to False.
        """
        prompt_name = "philosophies"
        pc = PromptConstructor(prompt_name=prompt_name, prompt_version_number=prompt_version_number)
        prompt = pc.get_prompt()
        history_key = self.get_key(prompt_name, pc.prompt_version_number)
        out = self.send_receive(prompt, history_key, force_refresh)
        self.philosophies = parse_structured_output(out)

    def set_actions_from_philosophies(
        self,
        philosophy_dict: dict,
        prompt_version_number: int,
        force_refresh: bool = False,
    ) -> None:
        """Determines the actions from a philosophy.

        Args:
            philosophy_dict (dict): A dictionary representing a philosophy.
            prompt_version_number (int): The version number of the prompt.
            force_refresh (bool, optional): If true, rerun even if history_key is in history. Defaults to False.
        """
        prompt_name = "action_from_philosophy"
        pc = PromptConstructor(prompt_name=prompt_name, prompt_version_number=prompt_version_number)
        prompt = pc.get_prompt(user_input=str(philosophy_dict))
        history_key = self.get_key(prompt_name, pc.prompt_version_number, philosophy_dict["name"])
        out = self.send_receive(prompt, history_key, force_refresh)
        self.actions_from_philosophies = parse_structured_output(out)

    def set_all_actions_from_philosophies(self) -> None:
        """Set all actions from all philosophies."""
        collect_actions_from_philosophies = []
        for philosophy_dict in self.philosophies:
            self.set_actions_from_philosophies(
                prompt_version_number=0,
                philosophy_dict=philosophy_dict,
            )
            collect_actions_from_philosophies.append(
                {
                    "philo": philosophy_dict,
                    "actions": self.actions_from_philosophies,
                }
            )
        self.all_actions_from_philosophies = collect_actions_from_philosophies

    def set_all_actions(self) -> None:
        """Collect all actions into a list."""
        collect_all_actions = []
        for action in self.all_actions_from_philosophies:
            for action_dict in action["actions"]:
                collect_all_actions.append(action_dict["action"])
        self.all_actions = collect_all_actions

    def set_clusters_to_actions(
        self,
        prompt_version_number: int,
        force_refresh: bool = False,
        pbar: bool = False,
        verbose: bool = False,
    ) -> None:
        """Create a dictionary of clusters to actions.

        Args:
            prompt_version_number (int): The version number of the prompt.
            force_refresh (bool, optional): If true, rerun even if history_key is in history. Defaults to False.
            pbar (bool, optional): If true, show a progress bar. Defaults to False.
            verbose (bool, optional): If true, log the prompt and response. Defaults to False.
        """
        prompt_name = "determine_clusters"
        pc = PromptConstructor(prompt_name=prompt_name, prompt_version_number=prompt_version_number)
        prompt = pc.get_prompt(user_input="\n".join(self.all_actions))
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
        iterator = self.all_actions
        if pbar:
            iterator = tqdm(self.all_actions)
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
        self.cluster_to_actions = self.cluster_to_actions_dict

    def set_cluster_to_actions_dict(self) -> None:
        """Create a dictionary of clusters to actions."""
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
        # Sort by the number of actions in each cluster
        collect = dict(sorted(collect.items(), key=lambda item: len(item[1]), reverse=True))
        self.cluster_to_actions_dict = collect

    def set_sorted_actions(self):
        """Create a list of sorted actions."""
        sorted_actions = []
        for value_dict in self.cluster_to_actions.values():
            for d in value_dict:
                sorted_actions.append(d["action"])
        self.sorted_actions = sorted_actions

    def set_action_scores(
        self,
        prompt_version_number: int,
        force_refresh: bool = False,
        pbar: bool = False,
        verbose: bool = False,
    ):
        """Create a list of action scores.

        Args:
            prompt_version_number (int): The version number of the prompt.
            force_refresh (bool, optional): If true, rerun even if history_key is in history. Defaults to False.
            pbar (bool, optional): If true, show a progress bar. Defaults to False.
            verbose (bool, optional): If true, log the prompt and response. Defaults to False.
        """
        prompt_name = "score_action"
        pc = PromptConstructor(prompt_name=prompt_name, prompt_version_number=prompt_version_number)
        self.collect_action_scores = []
        iterator = self.all_actions
        if pbar:
            iterator = tqdm(self.all_actions)
        for action in iterator:
            user_input = "{\n\t'action':'{{ ACTION }}'\n\t'philosophies':{{ PHILOSOPHIES }}\n}"
            user_input = user_input.replace("{{ ACTION }}", action)
            pl = str(self.philosophies)
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
        self.action_scores = self.collect_action_scores

    def create_scorecard(self) -> None:
        """Create a scorecard of the action scores."""
        # Convert the list of dictionaries into a DataFrame
        df = pd.DataFrame(self.action_scores)

        # Map morality to numerical values
        morality_map = {"moral": 1, "undecided": 0, "immoral": -1}
        df["morality_value"] = df["morality"].map(morality_map)
        df_pivot = df.pivot_table(
            values="morality_value",
            index="philosophy",
            columns="action",
            fill_value=-10,
        )

        # Sort philosophies by number of 1's, then by number of 0's, then by number of -1's
        philosophy_reindex = df_pivot.sum(axis=1).sort_values(ascending=False).index
        df_pivot = df_pivot.reindex(philosophy_reindex)

        df_pivot = df_pivot[self.sorted_actions]

        cluster_to_int = {k: e + 1 for e, k in enumerate(self.cluster_to_actions_dict.keys())}

        action_to_cluster = {
            d["action"]: f'{cluster_to_int[d["cluster"]]:2d}' for d in self.collect_action_clusters
        }

        actions = df_pivot.columns.to_list()
        actions = [f"{action_to_cluster[a]} | {a}" for a in actions]
        philosophies = df_pivot.index.to_list()

        # Custom hover data
        # Assuming df is your original DataFrame
        hover_data = df.pivot_table(
            values="reason",
            index="philosophy",
            columns="action",
            aggfunc=lambda x: ", ".join(x),  # Aggregate reasons, if necessary
        ).fillna("")

        hover_data = hover_data[self.sorted_actions]
        hover_data = hover_data.reindex(philosophy_reindex)

        philosophy_to_description = {row["name"]: row["description"] for row in self.philosophies}

        def hover_str(row, col):
            out = f"philosophy: {row.name}<br>"
            philosophy_description = philosophy_to_description[row.name]
            out += f"philosophy description: {philosophy_description}<br>"
            out += f"action: {col}<br>"
            out += f"reason: {row[col]}"
            return out

        # Format hover_data with philosophy, action, and reason
        hover_data = hover_data.apply(
            lambda row: row.index.map(lambda col: hover_str(row=row, col=col)),
            axis=1,
        )

        # Create the heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=df_pivot.values,
                x=actions,
                y=philosophies,
                hoverinfo="text",
                hovertext=hover_data.values,
                showscale=False,
                colorscale="Blues_r",
            )
        )

        fig.update_traces(text=hover_data.values, hoverinfo="text")

        cluster_to_int_str = (
            "<b><span style='text-decoration:underline;'>Cluster Labels</span></b><br>"
        )
        cluster_to_int_str += "<br>".join([f"{v:2d} | {k}" for k, v in cluster_to_int.items()])

        # Add annotation with the dictionary text
        fig.add_annotation(
            x=1.13,
            y=-0.60,
            xref="paper",
            yref="paper",
            text=cluster_to_int_str,
            showarrow=False,
            font=dict(size=12),
            align="left",
        )

        # Update layout for better readability
        fig.update_layout(title="Action Scores Heatmap", margin_r=275)

        fig.update_yaxes(autorange="reversed")

        # Colors for the legend (assuming these to represent min, mid, and max of 'Blues_r')
        colors = [
            "#f7fbff",  # Lightest blue for 'immoral'
            "#6baed6",  # Medium blue for 'undecided'
            "#08306b",
        ]  # Darkest blue for 'moral'

        # Add dummy traces for the legend items
        legend_labels = ["immoral", "undecided", "moral"]
        for color, label in zip(colors, legend_labels):
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(size=10, color=color),
                    legendgroup="group",
                    showlegend=True,
                    name=label,
                )
            )

        # Adjust layout if necessary
        fig.update_layout(legend_title_text="Category")

        # Save the figure
        # If the path doesn't exist, create it
        if not os.path.exists("results"):
            os.makedirs("results")
        ol.plot(fig, filename="results/action_scores_heatmap.html", auto_open=False)
