import os
from philo.utils import get_repo_root


class PromptConstructor:
    def __init__(self, prompt_name: str):
        self.repo_root = get_repo_root()
        self.prompt_name = prompt_name
        self.full_prompt_path = os.path.join(self.repo_root, "prompts", self.prompt_name)
        self.check_prompt_name()

    def check_prompt_name(self):
        # Check if self.prompt_name is a subdirectory of self.repo_root/prompts
        if not os.path.isdir(self.full_prompt_path):
            raise ValueError(f"{self.prompt_name} is not a valid prompt.")

    def set_prompt_parts(self):
        # Set the prompt parts
        self.prompt_parts = {}
        for file in os.listdir(self.full_prompt_path):
            if file.endswith(".prompt"):
                with open(os.path.join(self.full_prompt_path, file), "r") as f:
                    self.prompt_parts[file.replace(".prompt", "")] = f.read()
