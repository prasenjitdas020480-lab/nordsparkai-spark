import csv
import json
from typing import Any

from core.config import CONFIG_FILE, LEADS_FILE


def load_config() -> dict[str, Any]:
    """Load chatbot configuration from config.json."""

    if not CONFIG_FILE.exists():
        return {}

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_config(config: dict[str, Any]) -> None:
    """Save chatbot configuration to config.json."""

    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=False)


def save_lead(lead: dict[str, str]) -> None:
    """Append one lead to leads.csv."""

    file_exists = LEADS_FILE.exists()

    with LEADS_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=lead.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(lead)


def load_leads() -> list[dict[str, str]]:
    """Load all saved leads."""

    if not LEADS_FILE.exists():
        return []

    with LEADS_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))