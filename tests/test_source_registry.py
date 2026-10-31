import pytest

from intelligence.source_registry import (
    load_source_registry,
    get_sources_by_market,
)


def test_source_registry_loads_successfully():
    sources = load_source_registry()

    assert isinstance(sources, list)
    assert len(sources) > 0


def test_indian_sources_are_selected():
    sources = get_sources_by_market("INDIA")

    names = [source["name"] for source in sources]

    assert "Business Standard" in names
    assert "Mint" in names
    assert "Moneycontrol" in names
    assert "Wall Street Journal" not in names


def test_us_sources_are_selected():
    sources = get_sources_by_market("US")

    names = [source["name"] for source in sources]

    assert "Wall Street Journal" in names
    assert "Barron's" in names
    assert "Moneycontrol" not in names


def test_global_sources_are_selected():
    sources = get_sources_by_market("GLOBAL")

    names = [source["name"] for source in sources]

    assert "Reuters" in names
    assert "Bloomberg" in names
    assert "Financial Times" in names


def test_disabled_sources_are_excluded():
    sources = get_sources_by_market("INDIA")

    assert all(source["enabled"] for source in sources)


def test_sources_are_sorted_by_priority():
    sources = get_sources_by_market("INDIA")

    priorities = [source["priority"] for source in sources]

    assert priorities == sorted(priorities)


def test_invalid_market_is_rejected():
    with pytest.raises(ValueError, match="Unsupported market"):
        get_sources_by_market("EUROPE")