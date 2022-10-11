"""Module used to specify location of static files used as inputs when testing"""

# Standard library imports
from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / "test_data"
FIXTURE_DIR = Path(__file__).parents[1] / "data" / "fixtures"
