import json
import sqlite3
from pathlib import Path
import re

# ---------------------------
# Paths
# ---------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "instance" / "cats.db"
CAT_API_JSON = PROJECT_ROOT / "notebooks" / "cat_api_cleaned.json"
GERMAN_JSON = PROJECT_ROOT / "notebooks" / "german_cat_breed_info.json"

# ---------------------------
# Database helpers
# ---------------------------

def get_connection():
    """
    Open a DB connection
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ---------------------------
# JSON loading
# ---------------------------

def load_json(path: Path):
    """
    Load and return JSON from a file.
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------
# Text helpers
# ---------------------------

def clean_text(value):
    """
    Trim strings.
    Convert empty / whitespace-only strings to None.
    """
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None

def split_csv_field(value):
    """
    Split comma-separated strings into a list of cleaned values
    Returns an empty list if input is missing or empty
    """
    if not value:
        return []
    parts = value.split(",")
    return [p.strip() for p in parts if p.strip()]


# ---------------------------
# Parsing helpers
# ---------------------------

def parse_range(value):
    """
    Parse ranged values like metric_weight or life_span e.g.: 3 - 5
    Returns (min, max) or (None, None)
    """
    if not value:
        return None, None

    numbers = re.findall(r"\d+", str(value))
    if not numbers:
        return None, None

    if len(numbers) == 1:
        num = int(numbers[0])
        return num, num

    low, high = int(numbers[0]), int(numbers[1])
    return (low, high) if low <= high else (high, low)


# ---------------------------
# Image
# ---------------------------
def get_featured_image_from_cat_api(breed):
    """
    Extract image.url from Cat API breed object.
    """
    image = breed.get("image")
    if not image:
        return None
    return clean_text(image.get("url"))
