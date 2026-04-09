import os
import json
from loguru import logger

GOLD_STANDARD_FILE = "data/gold_standard.json"

def save_gold_standard(question: str, answer: str):
    """Saves a verified Q&A pair."""
    data = {}
    if os.path.exists(GOLD_STANDARD_FILE):
        try:
            with open(GOLD_STANDARD_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            pass

    data[question.strip().lower()] = answer

    os.makedirs(os.path.dirname(GOLD_STANDARD_FILE), exist_ok=True)
    with open(GOLD_STANDARD_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_gold_standard(question: str):
    """Retrieves a gold standard answer if it exists."""
    if not os.path.exists(GOLD_STANDARD_FILE):
        return None

    try:
        with open(GOLD_STANDARD_FILE, "r") as f:
            data = json.load(f)
            return data.get(question.strip().lower())
    except Exception:
        return None
