"""Unit tests for ML feature engineering functions."""

import pytest
from datetime import datetime, timezone, timedelta


import importlib.util
from pathlib import Path
ml_engine_path = Path(__file__).parent.parent.parent.parent / "ml-engine"
spec = importlib.util.spec_from_file_location(
    "feature_engineering",
    str(ml_engine_path / "app" / "features" / "feature_engineering.py")
)
fe_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fe_module)
compute_churn_features = fe_module.compute_churn_features
_parse_dt = fe_module._parse_dt


class TestComputeChurnFeatures:
    def _make_interaction(self, days_ago: int, itype: str = "email", sentiment: float = 0.7):
        dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
        return {
            "occurred_at": dt.isoformat(),
            "interaction_type": itype,
            "sentiment_score": sentiment,
        }

    def _make_customer(self, **kwargs):
        base = {
            "email": "test@example.com",
            "phone": "555-1234",
            "company": "Acme",
            "status": "active",
            "health_score": 75.0,
            "lead_score": 60,
            "lifetime_value": 5000.0,
            "created_at": (
                datetime.now(timezone.utc) - timedelta(days=365)
            ).isoformat(),
        }
        return {**base, **kwargs}

    def test_returns_dict(self):
        feats = compute_churn_features(self._make_customer(), [])
        assert isinstance(feats, dict)

    def test_no_interactions_sets_high_recency(self):
        feats = compute_churn_features(self._make_customer(), [])
        assert feats["days_since_last_interaction"] == 999

    def test_recent_interaction_lowers_recency(self):
        interactions = [self._make_interaction(2)]
        feats = compute_churn_features(self._make_customer(), interactions)
        assert feats["days_since_last_interaction"] <= 3

    def test_interaction_counts(self):
        interactions = [
            self._make_interaction(5),
            self._make_interaction(15),
            self._make_interaction(45),
            self._make_interaction(100),
        ]
        feats = compute_churn_features(self._make_customer(), interactions)
        assert feats["interaction_count_30d"] == 2
        assert feats["interaction_count_90d"] == 3

    def test_sentiment_averages(self):
        interactions = [
            self._make_interaction(5, sentiment=0.8),
            self._make_interaction(10, sentiment=0.6),
        ]
        feats = compute_churn_features(self._make_customer(), interactions)
        assert abs(feats["avg_sentiment_30d"] - 0.7) < 0.01

    def test_negative_sentiment_ratio(self):
        interactions = [
            self._make_interaction(5, sentiment=0.2),   # negative
            self._make_interaction(10, sentiment=0.9),  # positive
        ]
        feats = compute_churn_features(self._make_customer(), interactions)
        assert feats["negative_sentiment_ratio"] == 0.5

    def test_has_email_flag(self):
        feats = compute_churn_features(
            self._make_customer(email="a@b.com"), []
        )
        assert feats["has_email"] == 1

    def test_no_email_flag(self):
        feats = compute_churn_features(
            self._make_customer(email=None), []
        )
        assert feats["has_email"] == 0

    def test_log_lifetime_value_positive(self):
        feats = compute_churn_features(
            self._make_customer(lifetime_value=10000), []
        )
        assert feats["log_lifetime_value"] > 0

    def test_status_encoding(self):
        for status, expected in [("active", 1), ("inactive", 0), ("churned", -1)]:
            feats = compute_churn_features(
                self._make_customer(status=status), []
            )
            assert feats["status_encoded"] == expected

    def test_type_count_breakdown(self):
        interactions = [
            self._make_interaction(5, itype="call"),
            self._make_interaction(10, itype="call"),
            self._make_interaction(15, itype="meeting"),
        ]
        feats = compute_churn_features(self._make_customer(), interactions)
        assert feats["call_count_90d"] == 2
        assert feats["meeting_count_90d"] == 1
        assert feats["email_count_90d"] == 0


class TestParseDt:
    def test_parses_iso_string(self):
        dt_str = "2026-01-15T10:30:00+00:00"
        result = _parse_dt(dt_str)
        assert result.year == 2026
        assert result.month == 1

    def test_handles_none(self):
        result = _parse_dt(None)
        assert result.year == 1970

    def test_handles_datetime_object(self):
        dt = datetime(2026, 7, 1, tzinfo=timezone.utc)
        assert _parse_dt(dt) == dt
