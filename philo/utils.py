import os
import json
from typing import List, Dict

MessageType = List[Dict[str, str]]


# A method to get parent directory of the current file
def get_repo_root() -> str:
    """Get the root directory of the repository

    Returns:
        str: The absolute path to the root directory of the repository
    """
    out = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
    return out


import re
from ast import literal_eval


# Convert a string of text to a list of dictionaries
def parse_structured_output(text: str) -> any:
    """Parse a string of text into python objects

    Args:
        text (str): The text to parse

    Returns:
        any: The parsed text as a python object
    """
    out = text
    # Remove all lines that start with "#" and "`"
    # and remove any comments from the end of a line
    collect = []
    for line in out.split("\n"):
        if line.startswith("#") or line.startswith("`"):
            continue
        else:
            parsed_line = line
            if "#" in parsed_line:
                parsed_line = line[: line.index("#")]
            collect.append(parsed_line)
    out = "\n".join(collect)
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
    """Load the history from a file

    Args:
        suffix (str, optional): Use for different histories. Defaults to "".

    Returns:
        dict: The history
    """
    history_file_path = os.path.join(get_repo_root(), f"history{suffix}.json")
    with open(history_file_path, "r") as f:
        history = json.load(f)
    return history
