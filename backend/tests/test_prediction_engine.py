from dataclasses import dataclass

from app.services.analysis.prediction_engine import build_outcome_band


@dataclass
class FakeEvent:
    name: str
    unit: str
    previous: float
    consensus: float
    ai_estimate: float
    ai_estimate_low: float
    ai_estimate_high: float
    actual: float | None


def test_hot_print_reads_hawkish_and_big():
    cpi = FakeEvent(
        name="US CPI YoY", unit="%", previous=3.3, consensus=3.4,
        ai_estimate=3.42, ai_estimate_low=3.25, ai_estimate_high=3.55, actual=3.9,
    )
    band = build_outcome_band(cpi)
    assert band["magnitude"] == "big"
    assert band["policy_lean"] == "hawkish"
    assert band["inverted"] is False
    assert band["effective_z"] == band["actual_z"]  # not inverted, so effective == raw


def test_inverted_series_flips_policy_lean_not_magnitude():
    # A higher unemployment rate is a WORSE labor market -- dovish -- even
    # though the raw print is above consensus. This is the exact case the
    # spec called out: "jobless claims... correctly reads dovish despite
    # being a higher number, because inverted flips the policy lean."
    unemployment = FakeEvent(
        name="US Unemployment Rate", unit="%", previous=4.1, consensus=4.0,
        ai_estimate=3.98, ai_estimate_low=3.85, ai_estimate_high=4.15, actual=4.3,
    )
    band = build_outcome_band(unemployment)
    assert band["actual_z"] > 0          # raw print is above consensus
    assert band["policy_lean"] == "dovish"  # but reads dovish because inverted
    assert band["inverted"] is True
    assert band["effective_z"] == -band["actual_z"]  # position flips for charting


def test_in_line_print_is_neutral_and_small():
    pmi = FakeEvent(
        name="US ISM Manufacturing PMI", unit="idx", previous=48.5, consensus=48.8,
        ai_estimate=48.88, ai_estimate_low=48.65, ai_estimate_high=49.05, actual=48.82,
    )
    band = build_outcome_band(pmi)
    assert band["magnitude"] == "small"
    assert band["policy_lean"] == "neutral"


def test_unreleased_event_has_no_actual_z_or_lean():
    upcoming = FakeEvent(
        name="US CPI YoY", unit="%", previous=3.3, consensus=3.4,
        ai_estimate=3.42, ai_estimate_low=3.25, ai_estimate_high=3.55, actual=None,
    )
    band = build_outcome_band(upcoming)
    assert band["actual_z"] is None
    assert band["policy_lean"] is None
    assert band["ai_estimate_z"] is not None  # pre-release band still positions the AI estimate


def test_basis_is_always_flagged_heuristic():
    event = FakeEvent(
        name="US GDP QoQ Annualized", unit="%", previous=2.1, consensus=2.3,
        ai_estimate=2.3, ai_estimate_low=2.1, ai_estimate_high=2.5, actual=None,
    )
    band = build_outcome_band(event)
    assert band["basis"] == "heuristic"
    assert "not yet calibrated" in band["disclosure"]
