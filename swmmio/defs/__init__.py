# Standard library imports
import os
import json
import yaml
from swmmio.defs.sectionheaders import normalize_inp_config

_DEFS_PATH = os.path.abspath(os.path.dirname(__file__))
_HEADERS_JSON = os.path.join(_DEFS_PATH, 'section_headers.json')
_INP_SECTIONS_YAML = os.path.join(_DEFS_PATH, 'inp_sections.yml')

with open(_HEADERS_JSON, 'r') as f:
    HEADERS = json.load(f)

with open(_INP_SECTIONS_YAML, 'r') as f:
    _inp_sections_conf_raw = yaml.load(f)

INP_OBJECTS = normalize_inp_config(_inp_sections_conf_raw['inp_file_objects'])
INFILTRATION_COLS = _inp_sections_conf_raw['infiltration_cols']