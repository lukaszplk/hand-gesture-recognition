"""Initialize src package."""

from pathlib import Path

# Package metadata
__version__ = "1.0.0"
__author__ = "Your Name"

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))
