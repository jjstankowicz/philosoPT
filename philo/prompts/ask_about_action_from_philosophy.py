version[0] = """

"""
version[0] = version[0].replace("{{ FORMAT_STRING }}", FORMAT_STRING)
version[0] = version[0].replace("{{ EXAMPLE_STRING }}", EXAMPLE_STRING)
version[0] = version[0].replace("{{ USER_STRING }}", USER_STRING)

version[-1] = version[0]
