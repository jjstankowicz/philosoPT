version = {}

FORMAT_STRING = """
You can use a "scratchpad" to think about your answer before responding.
Every line of the scratchpad should start with a hashtag (#).
Your response should be a list of dictionaries
where each dictionary has an "action", a "moral" key, and a "reason" key.
"""

USER_STRING = """
===== QUESTION FOR YOU BELOW =====
Input:
```
{{ USER_INPUT }}
```
"""

EXAMPLE_STRING = """
===== EXAMPLE BELOW =====
Input:
```
{'name': 'Aristotelianism', 'description': 'The philosophical tradition that takes its defining inspiration from the work of Aristotle.'}
```

Your output:
```
### Scratchpad
# Aristotilean ethics studies vituous aspects of a person's character.
# A virtuous person should not lie, therefore lying is immoral.
# A virtuous person should be brave, therefore bravery is moral.
# A virtuous person should have a hard time deciding if others should live or die
# without knowing their virtues or vices,
# therefore they will have a hard time making a decision in the trolley car problem.
# ...

[
    {'action': 'lying', 'moral': 'immoral', 'reason': 'A virtuous person should not lie.'},
    {'action': 'bravery', 'moral': 'moral', 'reason': 'A virtuous person should be brave.'},
    ...
    ]
```
===== EXAMPLE ABOVE =====
"""

version[0] = """
I will give you a philosophy and a brief description of it. 
From your knowledge and the brief description, tell me:
- Two actions that can be described as moral from the philosophy
- Two actions that can be described as immoral from the philosophy
- Two actions that are difficult to describe as moral or immoral from the philosophy

{{ FORMAT_STRING }}

{{ EXAMPLE_STRING }}

{{ USER_STRING }}
"""
version[0] = version[0].replace("{{ FORMAT_STRING }}", FORMAT_STRING)
version[0] = version[0].replace("{{ EXAMPLE_STRING }}", EXAMPLE_STRING)
version[0] = version[0].replace("{{ USER_STRING }}", USER_STRING)

version[-1] = version[0]
