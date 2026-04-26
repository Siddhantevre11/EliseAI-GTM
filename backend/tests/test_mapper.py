import pytest
from ingestion.mapper import (
    detect_source,
    map_columns,
    transform_row,
    normalize_header,
    find_standard_field,
    COLUMN_ALIASES,
    SOURCE_SIGNATURES,
)


class TestNormalizeHeader:
    def test_basic_normalization(self):
        assert normalize_header("Company Name") == "company_name"
        assert normalize_header("billing city") == "billing_city"
        assert normalize_header("Account-Name") == "account_name"

    def test_empty_header(self):
        assert normalize_header("") == ""
        assert normalize_header(None) == ""

    def test_strip_whitespace(self):
        assert normalize_header("  Company  ") == "company"


class TestDetectSource:
    def test_salesforce_detection(self):
        headers = ["Account Name", "Billing City", "Billing State", "Account ID"]
        assert detect_source(headers) == "Salesforce"

    def test_salesforce_with_sfdc(self):
        headers = ["company", "city", "sfdc_id"]
        assert detect_source(headers) == "Salesforce"

    def test_hubspot_detection(self):
        headers = ["Company ID", "Contact ID", "HubSpot", "email"]
        assert detect_source(headers) == "HubSpot"

    def test_hubspot_with_hs_prefix(self):
        headers = ["hs_email", "hs_name", "company"]
        assert detect_source(headers) == "HubSpot"

    def test_apollo_detection(self):
        headers = ["Organization Name", "apollo_id", "email"]
        assert detect_source(headers) == "Apollo"

    def test_generic_csv_default(self):
        headers = ["company", "city", "state", "email"]
        assert detect_source(headers) == "Generic CSV"

    def test_linkedin_detection(self):
        headers = ["name", "LinkedIn Profile", "LinkedIn URL", "company"]
        assert detect_source(headers) == "LinkedIn"


class TestMapColumns:
    def test_salesforce_mapping(self):
        headers = ["Account Name", "Billing City", "Billing State", "Email"]
        mapping, unmapped = map_columns(headers)

        assert mapping["Account Name"] == "company"
        assert mapping["Billing City"] == "city"
        assert mapping["Billing State"] == "state"
        assert mapping["Email"] == "email"

    def test_apollo_mapping(self):
        headers = ["Organization Name", "Location", "email address"]
        mapping, unmapped = map_columns(headers)

        assert mapping["Organization Name"] == "company"
        assert mapping["Location"] == "city"
        assert mapping["email address"] == "email"

    def test_generic_mapping(self):
        headers = ["company", "city", "state", "email", "phone"]
        mapping, unmapped = map_columns(headers)

        assert mapping["company"] == "company"
        assert mapping["city"] == "city"
        assert mapping["state"] == "state"
        assert mapping["email"] == "email"
        assert mapping["phone"] == "phone"

    def test_unmapped_columns_reported(self):
        headers = ["company", "custom_field", "unknown_column"]
        mapping, unmapped = map_columns(headers)

        assert "company" not in unmapped
        assert "custom_field" in unmapped
        assert "unknown_column" in unmapped


class TestFindStandardField:
    def test_exact_match(self):
        assert find_standard_field("company") == "company"
        assert find_standard_field("email") == "email"

    def test_alias_match(self):
        assert find_standard_field("Account Name") == "company"
        assert find_standard_field("Organization Name") == "company"
        assert find_standard_field("billing city") == "city"

    def test_no_match(self):
        assert find_standard_field("xyz123") is None
        assert find_standard_field("") is None


class TestTransformRow:
    def test_basic_transform(self):
        row = {"company": "Acme", "city": "Austin", "email": "test@test.com"}
        mapping = {"company": "company", "city": "city", "email": "email"}

        result = transform_row(row, mapping, "Salesforce")

        assert result["company"] == "Acme"
        assert result["city"] == "Austin"
        assert result["email"] == "test@test.com"
        assert result["source"] == "Salesforce"
        assert "original_data" in result

    def test_strips_whitespace(self):
        row = {"company": "  Acme  ", "city": "  Austin  "}
        mapping = {"company": "company", "city": "city"}

        result = transform_row(row, mapping, "Generic CSV")

        assert result["company"] == "Acme"
        assert result["city"] == "Austin"

    def test_empty_string_becomes_none(self):
        row = {"company": "Acme", "city": ""}
        mapping = {"company": "company", "city": "city"}

        result = transform_row(row, mapping, "Generic CSV")

        assert result["city"] is None

    def test_preserves_original_data(self):
        row = {"company": "Acme", "city": "Austin"}
        mapping = {"company": "company", "city": "city"}

        result = transform_row(row, mapping, "Generic CSV")

        assert result["original_data"]["company"] == "Acme"
        assert result["original_data"]["city"] == "Austin"