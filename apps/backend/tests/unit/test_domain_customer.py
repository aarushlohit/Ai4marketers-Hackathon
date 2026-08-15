"""Unit tests for the Customer domain entity."""

import pytest
from uuid import uuid4
from app.domain.entities.customer import CustomerEntity


class TestCustomerEntity:
    def test_full_name(self):
        c = CustomerEntity(first_name="Jane", last_name="Doe")
        assert c.full_name == "Jane Doe"

    def test_full_name_strips_whitespace(self):
        c = CustomerEntity(first_name="Jane", last_name="")
        assert c.full_name == "Jane"

    def test_churn_risk_level_high(self):
        c = CustomerEntity(churn_probability=0.75)
        assert c.churn_risk_level == "high"

    def test_churn_risk_level_medium(self):
        c = CustomerEntity(churn_probability=0.5)
        assert c.churn_risk_level == "medium"

    def test_churn_risk_level_low(self):
        c = CustomerEntity(churn_probability=0.2)
        assert c.churn_risk_level == "low"

    def test_churn_risk_level_unknown(self):
        c = CustomerEntity(churn_probability=None)
        assert c.churn_risk_level == "unknown"

    def test_lead_grade_a(self):
        c = CustomerEntity(lead_score=85)
        assert c.lead_grade == "A"

    def test_lead_grade_f(self):
        c = CustomerEntity(lead_score=20)
        assert c.lead_grade == "F"

    def test_lead_grade_none(self):
        c = CustomerEntity(lead_score=None)
        assert c.lead_grade == "–"

    def test_deactivate(self):
        c = CustomerEntity(status="active")
        c.deactivate()
        assert c.status == "inactive"

    def test_mark_churned(self):
        c = CustomerEntity(status="active")
        c.mark_churned()
        assert c.status == "churned"

    def test_soft_delete(self):
        c = CustomerEntity()
        c.soft_delete()
        assert c.is_deleted is True

    def test_update_scores_clamps_churn(self):
        c = CustomerEntity()
        c.update_scores(churn_probability=1.5)
        assert c.churn_probability == 1.0

    def test_update_scores_clamps_health(self):
        c = CustomerEntity()
        c.update_scores(health_score=150.0)
        assert c.health_score == 100.0

    def test_update_scores_clamps_lead(self):
        c = CustomerEntity()
        c.update_scores(lead_score=-10)
        assert c.lead_score == 0

    def test_is_at_risk_high_churn(self):
        c = CustomerEntity(churn_probability=0.8)
        assert c.is_at_risk() is True

    def test_is_at_risk_low_churn(self):
        c = CustomerEntity(churn_probability=0.1)
        assert c.is_at_risk() is False
