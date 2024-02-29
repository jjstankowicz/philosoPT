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
    pattern = r"(\w)'(\w)"
    replacement = r"\1APOSTROPHEAPOSTROPHE\2"
    # Remove newlines
    out = text.replace("\n", "")
    # Replace single quotes with escaped single quotes
    out = re.sub(pattern, replacement, out)
    # Replace 'APOTROPHEAPOSTROPHE' with escaped single quotes
    out = out.replace("APOSTROPHEAPOSTROPHE", "\\'")
    out = literal_eval(out)
    return out
