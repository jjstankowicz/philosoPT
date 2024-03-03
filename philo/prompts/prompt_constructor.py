import os
from typing import Optional
from philo.utils import get_repo_root


class PromptConstructor:
    def __init__(self, prompt_name: str, prompt_version_number: int = 0):
        self.repo_root = get_repo_root()
        self.prompt_name = prompt_name
        self.prompt_version_number = prompt_version_number
        self.full_prompt_path = os.path.join(
            self.repo_root,
            "philo",
            "prompts",
            self.prompt_name,
            f"v{prompt_version_number}",
        )
        self.check_prompt_name()
        self.prompt_modifiers = ["format_string", "example_string", "user_string"]

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

    def get_prompt(self, user_input: Optional[str] = None) -> str:
        # Set the prompt parts
        self.set_prompt_parts()
        # Check if user_input is required
        user_input_required = "user_string" in self.prompt_parts
        if user_input is None and user_input_required:
            raise ValueError("user_input is required for this prompt.")
        # Get the base prompt
        out = self.prompt_parts["base"]
        # Modify the prompt according to the prompt modifiers
        for prompt_modifier in self.prompt_modifiers:
            if prompt_modifier not in self.prompt_parts:
                continue
            prompt_modifier_flag = prompt_modifier.upper()
            prompt_modifier_flag = "{{ " + prompt_modifier_flag + " }}"
            out = out.replace(prompt_modifier_flag, self.prompt_parts[prompt_modifier])
        # Replace the user input
        if user_input_required:
            out = out.replace("{{ USER_INPUT }}", user_input)
        return out
