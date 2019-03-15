# Standard library imports
import os
import json

_DEFS_PATH = os.path.abspath(os.path.dirname(__file__))
_HEADERS_JSON = os.path.join(_DEFS_PATH, 'section_headers.json')

with open(_HEADERS_JSON, 'r') as f:
    HEADERS = json.load(f)
