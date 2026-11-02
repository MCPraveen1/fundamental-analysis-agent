import pytest

from intelligence.source_registry import (
    load_source_registry,
    get_sources_by_market,
)

from intelligence.source_registry import (
    load_source_registry,
    get_sources_by_market,
    resolve_article_source,
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


def test_resolve_known_publisher():
    result = resolve_article_source(
        "https://www.reuters.com/markets/stocks/example"
    )

    assert result["publisher_name"] == "Reuters"
    assert result["source_domain"] == "reuters.com"
    assert result["source_type"] == "financial_news"
    assert result["source_verified"] is True


def test_resolve_publisher_subdomain():
    result = resolve_article_source(
        "https://uk.reuters.com/markets/example"
    )

    assert result["publisher_name"] == "Reuters"
    assert result["source_verified"] is True


def test_unknown_publisher():
    result = resolve_article_source(
        "https://example.com/financial-news"
    )

    assert result["publisher_name"] is None
    assert result["source_domain"] == "example.com"
    assert result["source_type"] == "unknown"
    assert result["source_verified"] is False


def test_invalid_url():
    result = resolve_article_source("not-a-valid-url")

    assert result["publisher_name"] is None
    assert result["source_type"] == "unknown"
    assert result["source_verified"] is False


def test_missing_url():
    result = resolve_article_source("")

    assert result["publisher_name"] is None
    assert result["source_domain"] is None
    assert result["source_type"] == "unknown"
    assert result["source_verified"] is False


def test_domain_spoofing_is_rejected():
    result = resolve_article_source(
        "https://fake-reuters.com/financial-news"
    )

    assert result["publisher_name"] is None
    assert result["source_type"] == "unknown"
    assert result["source_verified"] is False