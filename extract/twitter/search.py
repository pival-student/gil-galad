import json
import re
import os
from tqdm import tqdm

SAMPLE_FILE_PATTERN = r'samples__\d+\.txt'
HIT_FILE_PATTERN = r'hits__\d+\.txt'

SEARCH_CFG = 'search.json'
SEARCH_DIR = os.path.join('..', 'data', 'out', 'run1')




