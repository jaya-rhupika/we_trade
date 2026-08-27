import json
from pathlib import Path
from typing import Any

import pytest

from analytics_etl.transform import transform


FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def load_fixture():
    def load(name: str) -> dict[str, Any]:
        with (FIXTURES / name).open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)

    return load


def _valid_rows(result: Any) -> list[dict[str, Any]]:
    return result["valid_rows"]


def _rejected_rows(result: Any) -> list[dict[str, Any]]:
    return result["rejected_rows"]


def _rejected_for(result: Any, date: str) -> list[dict[str, Any]]:
    return [row for row in _rejected_rows(result) if row.get("date") == date]


def test_transform_is_importable():
    assert callable(transform)


def test_valid_fixture_transforms_to_loadable_rows(load_fixture):
    result = transform(load_fixture("candles-reliance-ns-2026-07.json"))

    rows = _valid_rows(result)
    first = next(row for row in rows if row["date"] == "2026-07-01")
    assert len(rows) == 9
    assert first["symbol"] == "RELIANCE.NS"
    assert first["open"] == 2864.0
    assert first["high"] == 2881.35
    assert first["low"] == 2857.2
    assert first["close"] == 2876.9
    assert first["volume"] == 5412700
    assert isinstance(first["date"], str)
    assert isinstance(first["close"], (int, float))
    assert isinstance(first["volume"], int)
    assert _rejected_rows(result) == []


def test_malformed_rows_are_quarantined_with_reasons(load_fixture):
    result = transform(load_fixture("candles-malformed.json"))

    expected_rejections = {
        "2026-07-01": "conflicting duplicate",
        "2026-07-02": "missing close",
        "2026-07-06": "numeric",
        "2026-07-07": "high",
        "2026-07-08": "volume",
        "09/07/2026": "ISO date",
    }
    rejected = _rejected_rows(result)
    for date, reason_fragment in expected_rejections.items():
        matching = _rejected_for(result, date)
        assert matching, f"expected {date} to be rejected"
        assert any(reason_fragment.lower() in row["reason"].lower() for row in matching)

    valid_dates = {row["date"] for row in _valid_rows(result)}
    assert "2026-07-01" not in valid_dates
    assert "2026-07-02" not in valid_dates
    assert "2026-07-06" not in valid_dates
    assert "2026-07-07" not in valid_dates
    assert "2026-07-08" not in valid_dates
    assert "09/07/2026" not in valid_dates
    assert "2026-07-03" in valid_dates


def test_rejects_a_high_below_a_low(load_fixture):
    result = transform(load_fixture("candles-malformed.json"))

    assert _rejected_for(result, "2026-07-07")
    assert all(row["date"] != "2026-07-07" for row in _valid_rows(result))


def test_empty_candles_response_produces_empty_valid_dataset():
    raw_response = {
        "data": {
            "symbol": "TATASTEEL.BO",
            "interval": "1d",
            "currency": "INR",
            "candles": [],
        },
        "meta": {
            "asOf": "2026-07-10T06:00:00Z",
            "disclaimer": "Educational data. Not for investment use.",
            "symbol": "TATASTEEL.BO",
            "source": "stored",
        },
    }

    result = transform(raw_response)

    assert _valid_rows(result) == []
    assert _rejected_rows(result) == []
