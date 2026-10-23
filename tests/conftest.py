"""Shared helpers for all test files."""
import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"


def read_csv(filename):
    """Read a CSV file from test_data/ and return a list of dict rows."""
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
