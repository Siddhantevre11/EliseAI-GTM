import pytest
from schemas.lead import Lead, STATE_MAP


class TestLeadSchema:
    def test_basic_lead_creation(self):
        lead = Lead(company="Acme Corp", city="Austin", state="TX")
        assert lead.company == "Acme Corp"
        assert lead.city == "Austin"
        assert lead.state == "TX"
        assert lead.source == "unknown"
        assert lead.requires_review is False

    def test_state_coercion_full_name(self):
        lead = Lead(company="Acme Corp", city="Austin", state="Texas")
        assert lead.state == "TX"

    def test_state_coercion_lowercase(self):
        lead = Lead(company="Acme Corp", city="Austin", state="texas")
        assert lead.state == "TX"

    def test_state_coercion_already_2_letter(self):
        lead = Lead(company="Acme Corp", city="Austin", state="tx")
        assert lead.state == "TX"

    def test_state_missing_returns_placeholder(self):
        lead = Lead(company="Acme Corp", city="Austin", state="")
        assert lead.state == "[MISSING_STATE]"
        assert lead.requires_review is True

    def test_state_invalid_returns_placeholder(self):
        lead = Lead(company="Acme Corp", city="Austin", state="UnknownState")
        assert lead.state == "[MISSING_STATE]"
        assert lead.requires_review is True

    def test_email_validation_valid(self):
        lead = Lead(company="Acme Corp", city="Austin", state="TX", email="test@acme.com")
        assert lead.email == "test@acme.com"
        assert lead.is_email_valid() is True

    def test_email_validation_invalid(self):
        lead = Lead(company="Acme Corp", city="Austin", state="TX", email="notanemail")
        assert lead.is_email_valid() is False

    def test_email_validation_empty(self):
        lead = Lead(company="Acme Corp", city="Austin", state="TX", email="")
        assert lead.email is None

    def test_original_data_stored(self):
        original = {"Account Name": "Acme Corp", "Billing City": "Austin"}
        lead = Lead(
            company="Acme Corp",
            city="Austin",
            state="TX",
            source="Salesforce",
            original_data=original,
        )
        assert lead.original_data == original

    def test_optional_fields_default_none(self):
        lead = Lead(company="Acme Corp", city="Austin", state="TX")
        assert lead.name is None
        assert lead.email is None
        assert lead.property_address is None
        assert lead.phone is None
        assert lead.website is None

    def test_extra_fields_allowed(self):
        lead = Lead(
            company="Acme Corp",
            city="Austin",
            state="TX",
            custom_field="custom_value",
        )
        assert lead.custom_field == "custom_value"


class TestStateMapping:
    def test_all_states_have_codes(self):
        assert "texas" in STATE_MAP
        assert STATE_MAP["texas"] == "TX"

    def test_state_map_count(self):
        assert len(STATE_MAP) >= 50