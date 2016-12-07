import os

# This is the swmmio project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

#path to the SWMM5 executable used within the run_models module
SWMM_ENGINE_PATH = os.path.join(ROOT_DIR, 'swmm5_engines', 'swmm5_22.exe')
