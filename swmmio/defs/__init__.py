# Standard library imports
import os
import json
import yaml

_DEFS_PATH = os.path.abspath(os.path.dirname(__file__))
_HEADERS_JSON = os.path.join(_DEFS_PATH, 'section_headers.json')
_INP_SECTIONS_YAML = os.path.join(_DEFS_PATH, 'inp_sections.yml')

with open(_HEADERS_JSON, 'r') as f:
    HEADERS = json.load(f)

with open(_INP_SECTIONS_YAML, 'r') as f:
    INP_SECTIONS = yaml.load(f)

INP_OBJECTS = INP_SECTIONS['inp_file_objects']
print(INP_SECTIONS)
INP_SECTION_TAGS = HEADERS['inp_section_tags']