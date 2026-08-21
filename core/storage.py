import json
from typing import Any

import requests
import streamlit as st

from core.config import CONFIG_FILE


def load_config() -> dict[str, Any]:
    """Load chatbot configuration from config.json."""

    if not CONFIG_FILE.exists():
        return {}

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_config(config: dict[str, Any]) -> None:
    """Save chatbot configuration to config.json."""

    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            config,
            file,
            indent=2,
            ensure_ascii=False,
        )


def _get_leads_api_url() -> str:
    """Return the production NordSparkAI Leads API URL."""

    return st.secrets["LEADS_API_URL"]


def save_lead(lead: dict[str, str]) -> None:
    """
    Send a captured lead to the NordSparkAI Leads API.

    The tenant_key identifies which customer/business
    owns the lead.
    """

    config = load_config()

    tenant_key = (
        config
        .get("business", {})
        .get("tenant_key", "")
        .strip()
    )

    if not tenant_key:
        raise RuntimeError(
            "tenant_key is missing from business configuration."
        )

    payload = {
        "tenant_key": tenant_key,
        "name": lead.get("Name", "").strip(),
        "company": lead.get("Company", "").strip(),
        "email": lead.get("Email", "").strip(),
        "phone": lead.get("Phone", "").strip(),
        "requirement": lead.get("Requirement", "").strip(),
    }

    response = requests.post(
        _get_leads_api_url(),
        json=payload,
        timeout=15,
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("success"):
        raise RuntimeError(
            result.get(
                "error",
                "Unable to save lead.",
            )
        )


def load_leads() -> list[dict[str, str]]:
    """
    Lead retrieval will be connected separately
    to the protected production dashboard API.
    """

    return []