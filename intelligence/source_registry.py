from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_CONFIG_PATH = PROJECT_ROOT / "config" / "news_sources.yaml"


def load_source_registry():
    """Load and validate the financial news source registry."""

    if not SOURCE_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"News source configuration not found: {SOURCE_CONFIG_PATH}"
        )

    with SOURCE_CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    sources = config.get("sources")

    if not isinstance(sources, list):
        raise ValueError(
            "News source configuration must contain a sources list."
        )

    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Each source must be a dictionary.")

        required_fields = {
            "name",
            "domain",
            "markets",
            "source_type",
            "priority",
            "enabled",
        }

        missing_fields = required_fields - source.keys()

        if missing_fields:
            raise ValueError(
                f"Source is missing required fields: {missing_fields}"
            )

    return sources


def get_sources_by_market(market):
    """Return enabled sources applicable to the requested market."""

    market = market.strip().upper()

    if market not in {"US", "INDIA", "GLOBAL"}:
        raise ValueError(f"Unsupported market: {market}")

    sources = load_source_registry()

    selected_sources = [
        source
        for source in sources
        if source["enabled"]
        and market in source["markets"]
    ]

    return sorted(
        selected_sources,
        key=lambda source: source["priority"],
    )