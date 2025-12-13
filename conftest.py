"""
PyTest configuration file for SchedularV3.
This file ensures that the project root is in the Python path,
allowing imports from core and utils packages.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

