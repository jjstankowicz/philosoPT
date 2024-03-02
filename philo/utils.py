import os
import json
from typing import List, Dict

MessageType = List[Dict[str, str]]


# A method to get parent directory of the current file
def get_repo_root() -> str:
    out = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
    return out


import re
from ast import literal_eval


# Convert a string of text to a list of dictionaries
def parse_structured_output(text: str) -> any:
    out = text
    # Remove all lines that start with "#"
    out = "\n".join(
        [line for line in out.split("\n") if not line.startswith("#") and not line.startswith("`")]
    )
    pattern = r"(\w)'(\w)"
    replacement = r"\1APOSTROPHEAPOSTROPHE\2"
    # Remove newlines
    out = out.replace("\n", "")
    # Replace single quotes with escaped single quotes
    out = re.sub(pattern, replacement, out)
    # Replace 'APOTROPHEAPOSTROPHE' with escaped single quotes
    out = out.replace("APOSTROPHEAPOSTROPHE", "\\'")
    out = out.replace("```", "")
    out = literal_eval(out)
    return out


def load_history(suffix: str = "") -> dict:
    history_file_path = os.path.join(get_repo_root(), f"history{suffix}.json")
    with open(history_file_path, "r") as f:
        history = json.load(f)
    return history
