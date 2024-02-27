import os
from typing import List, Dict

MessageType = List[Dict[str, str]]

# A method to get parent directory of the current file
def get_repo_root() -> str:
    out = os.path.abspath(os.path.join(__file__,os.pardir,os.pardir))
    return out

# A method to get the prompt from a file
def get_prompt(prompt_name: str, version_number: int) -> str:
    prompts_path = os.path.join(get_repo_root(), "prompts")
    # Import the file
    with open(os.path.join(prompts_path, f"{prompt_name}.py"), "r") as f:
        exec(f.read(), globals())
    # Return the version
    return version[version_number]