import os
from typing import List, Dict

MessageType = List[Dict[str, str]]


# A method to get parent directory of the current file
def get_repo_root() -> str:
    out = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
    return out


import re
from ast import literal_eval


# Convert a string of text to a list of dictionaries
def text_to_list_of_dicts(text: str) -> List[Dict[str, str]]:
    out = text
    if "##" in text:
        # Identify the last line that starts with "#"
        last_line = text.split("\n")
        last_line = [line for line in last_line if line.startswith("#")]
        last_line = last_line[-1]
        out = out.split(last_line)[-1]
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
