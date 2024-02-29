import os
from philo.utils import get_repo_root


class PromptConstructor:
    def __init__(self, prompt_name: str):
        self.repo_root = get_repo_root()
        self.prompt_name = prompt_name
        self.full_prompt_path = os.path.join(self.repo_root, "philo", "prompts", self.prompt_name)
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

    def get_prompt(self, user_input: str, prompt_version_number: int = 0) -> str:
        # Get the prompt
        self.set_prompt_parts()
        out = self.prompt_parts[f"v{prompt_version_number}"]
        for prompt_modifier in self.prompt_modifiers:
            if prompt_modifier not in self.prompt_parts:
                continue
            prompt_modifier_flag = f"{{ {prompt_modifier.upper()} }}"
            out = out.replace(prompt_modifier_flag, self.prompt_parts[prompt_modifier])
        # Replace the user input
        out = out.replace("{{ USER_INPUT }}", user_input)
        return out
