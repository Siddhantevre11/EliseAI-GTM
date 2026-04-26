import pytest
import tempfile
import os
from parsers.unified_parser import UnifiedParser, ParseResult, ParseError


class TestUnifiedParser:
    def setup_method(self):
        self.parser = UnifiedParser()

    # === Basic CSV Tests ===

    def test_parse_csv_basic(self):
        csv_content = """company,city,state,email
Acme Corp,Austin,TX,test@acme.com
Tech Inc,San Francisco,CA,info@tech.com"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert isinstance(result, ParseResult)
            assert len(result.leads) == 2
            assert result.stats["processed"] == 2
            assert result.stats["by_source"]["Generic CSV"] == 2
        finally:
            os.unlink(temp_path)

    def test_parse_csv_missing_company_logs_error(self):
        csv_content = """company,city,state,email
,Austin,TX,test@acme.com
Tech Inc,San Francisco,CA,info@tech.com"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert len(result.errors) == 1
            assert "Missing required field" in result.errors[0].error_message
        finally:
            os.unlink(temp_path)

    def test_parse_salesforce_export(self):
        csv_content = """Account Name,Billing City,Billing State,Email Address
Acme Corp,Austin,TX,test@acme.com
Tech Inc,San Francisco,CA,info@tech.com"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 2
            assert result.stats["by_source"]["Salesforce"] == 2
            assert result.leads[0].company == "Acme Corp"
        finally:
            os.unlink(temp_path)

    def test_self_healing_missing_state(self):
        csv_content = """company,city,state,email
Acme Corp,Austin,,test@acme.com"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.leads[0].state == "[MISSING_STATE]"
            assert result.leads[0].requires_review is True
        finally:
            os.unlink(temp_path)

    def test_self_healing_invalid_email(self):
        csv_content = """company,city,state,email
Acme Corp,Austin,TX,notanemail"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.leads[0].requires_review is True
        finally:
            os.unlink(temp_path)

    def test_parse_raw_data(self):
        headers = ["company", "city", "state", "email"]
        rows = [
            {"company": "Acme Corp", "city": "Austin", "state": "TX", "email": "test@acme.com"},
            {"company": "Tech Inc", "city": "SF", "state": "CA", "email": "info@tech.com"},
        ]

        result = self.parser.parse_raw_data(headers, rows)

        assert len(result.leads) == 2
        assert result.stats["processed"] == 2

    def test_parse_raw_data_empty(self):
        result = self.parser.parse_raw_data([], [])

        assert len(result.leads) == 0
        assert len(result.errors) == 0
        assert result.stats["total"] == 0

    def test_state_coercion_in_parser(self):
        csv_content = """company,city,state,email
Acme Corp,Austin,Texas,test@acme.com"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.leads[0].state == "TX"
        finally:
            os.unlink(temp_path)

    def test_original_data_preserved(self):
        csv_content = """Account Name,Billing City,Billing State
Acme Corp,Austin,TX"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert "Account Name" in result.leads[0].original_data
            assert result.leads[0].original_data["Account Name"] == "Acme Corp"
        finally:
            os.unlink(temp_path)

    def test_extract_sheet_id(self):
        url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
        sheet_id = self.parser._extract_sheet_id(url)
        assert sheet_id == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

    def test_extract_sheet_id_alternate_format(self):
        url = "https://docs.google.com/spreadsheets/d/abc123def456/edit"
        sheet_id = self.parser._extract_sheet_id(url)
        assert sheet_id == "abc123def456"

    def test_extract_sheet_id_invalid_url(self):
        url = "https://example.com/not-a-sheet"
        sheet_id = self.parser._extract_sheet_id(url)
        assert sheet_id is None


class TestFileFormats:
    def setup_method(self):
        self.parser = UnifiedParser()

    def test_parse_tsv_format(self):
        tsv_content = "company\tcity\tstate\temail\nAcme Corp\tAustin\tTX\ttest@acme.com"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
            f.write(tsv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.leads[0].company == "Acme Corp"
            assert result.leads[0].city == "Austin"
        finally:
            os.unlink(temp_path)

    def test_parse_csv_with_bom(self):
        csv_content = "company,city,state,email\nAcme Corp,Austin,TX,test@acme.com"
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            f.write(b'\xef\xbb\xbf' + csv_content.encode('utf-8'))
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.leads[0].company == "Acme Corp"
        finally:
            os.unlink(temp_path)

    def test_parse_csv_utf16_encoding(self):
        csv_content = "company,city,state,email\nAcme Corp,Austin,TX,test@acme.com"
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            f.write(csv_content.encode('utf-16'))
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
        except Exception as e:
            assert "encoding" in str(e).lower() or "utf" in str(e).lower()
        finally:
            os.unlink(temp_path)

    def test_parse_csv_windows_encoding(self):
        csv_content = "company,city,state,email\nAcme Corp,Austin,TX,test@acme.com"
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            f.write(csv_content.encode('cp1252'))
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.leads[0].company == "Acme Corp"
        finally:
            os.unlink(temp_path)

    def test_parse_csv_different_line_endings(self):
        csv_content = "company,city,state,email\r\nAcme Corp,Austin,TX,test@acme.com\r\nTech Inc,SF,CA,info@tech.com"
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            f.write(csv_content.encode('utf-8'))
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 2
        finally:
            os.unlink(temp_path)


class TestEdgeCases:
    def setup_method(self):
        self.parser = UnifiedParser()

    def test_parse_one_row_only(self):
        csv_content = "company,city,state,email\nAcme Corp,Austin,TX,test@acme.com"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.stats["total"] == 1
        finally:
            os.unlink(temp_path)

    def test_parse_header_only(self):
        csv_content = "company,city,state,email"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 0
            assert result.stats["processed"] == 0
        finally:
            os.unlink(temp_path)

    def test_parse_unicode_characters(self):
        csv_content = "company,city,state,email\nCafé Néo,Austín,TX,test@café.com\nMötley Crüe,München,DE,test@metal.com"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 2
            assert "Café" in result.leads[0].company
        finally:
            os.unlink(temp_path)

    def test_parse_headers_with_spaces(self):
        csv_content = " Company , City , State , Email \nAcme Corp,Austin,TX,test@acme.com"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.leads[0].company == "Acme Corp"
        finally:
            os.unlink(temp_path)

    def test_parse_headers_with_special_chars(self):
        csv_content = "Company [Required],City (City),State/Province,Email*"
        csv_content += "\nAcme Corp,Austin,TX,test@acme.com"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
        finally:
            os.unlink(temp_path)

    def test_parse_all_required_fields_missing(self):
        csv_content = "company,city,state,email\n,,,\nValid Corp,Austin,TX,test@valid.com"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert len(result.errors) == 1
            assert result.stats["skipped"] == 1
        finally:
            os.unlink(temp_path)

    def test_parse_whitespace_only_values(self):
        csv_content = "company,city,state,email\n   ,   ,   ,   \nValid Corp,Austin,TX,test@valid.com"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert len(result.errors) == 1
        finally:
            os.unlink(temp_path)


class TestSourceDetection:
    def setup_method(self):
        self.parser = UnifiedParser()

    def test_detect_hubspot_export(self):
        csv_content = "Company ID,Contact ID,HubSpot,Email\n1,100,Yes,test@acme.com"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.stats["by_source"]["HubSpot"] == 1
        finally:
            os.unlink(temp_path)

    def test_detect_apollo_export(self):
        csv_content = "Organization Name,apollo_id,Email\nAcme Corp,12345,test@acme.com"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
            assert result.stats["by_source"]["Apollo"] == 1
        finally:
            os.unlink(temp_path)

    def test_detect_linkedin_export(self):
        csv_content = "Name,LinkedIn Profile,Company\nJohn Doe,linkedin.com/in/johndoe,Acme Corp"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert len(result.leads) == 1
        finally:
            os.unlink(temp_path)


class TestParseResult:
    def test_stats_calculation(self):
        from schemas.lead import Lead

        leads = [
            Lead(company="Acme", city="Austin", state="TX", source="Salesforce"),
            Lead(company="Tech", city="SF", state="CA", source="Generic CSV"),
        ]
        errors = [ParseError(row_num=1, row_data={}, error_message="test error")]

        result = ParseResult(leads=leads, errors=errors)

        assert result.stats["total"] == 3
        assert result.stats["processed"] == 2
        assert result.stats["skipped"] == 1
        assert result.stats["by_source"]["Salesforce"] == 1
        assert result.stats["by_source"]["Generic CSV"] == 1