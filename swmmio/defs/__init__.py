# Standard library imports
import os
import yaml
from swmmio.defs.sectionheaders import normalize_inp_config

_DEFS_PATH = os.path.abspath(os.path.dirname(__file__))
_HEADERS_YAML = os.path.join(_DEFS_PATH, 'section_headers.yml')
_INP_SECTIONS_YAML = os.path.join(_DEFS_PATH, 'inp_sections.yml')

with open(_INP_SECTIONS_YAML, 'r') as f:
    _inp_sections_conf_raw = yaml.safe_load(f)

with open(_HEADERS_YAML, 'r') as f:
    HEADERS_YML = yaml.safe_load(f)

INP_OBJECTS = normalize_inp_config(_inp_sections_conf_raw['inp_file_objects'])
RPT_OBJECTS = normalize_inp_config(HEADERS_YML['rpt_sections'])
SWMM5_VERSION = HEADERS_YML['swmm5_version']
INP_SECTION_TAGS = _inp_sections_conf_raw['inp_section_tags']
INFILTRATION_COLS = _inp_sections_conf_raw['infiltration_cols']
COMPOSITE_OBJECTS = HEADERS_YML['composite']
INFILTRATION_KEY = 'INFILTRATION'
