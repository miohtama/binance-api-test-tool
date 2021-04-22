"""Console helpers"""
import json
from pygments import highlight, lexers, formatters


def print_colorful_json(data: dict):
    # https://stackoverflow.com/a/32166163/315168
    formatted_json = json.dumps(data, sort_keys=True, indent=4)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)
