from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import csv
import json
import re
import pandas as pd

from schemas.lead import Lead
from ingestion.mapper import detect_source, map_columns, transform_row


@dataclass
class ParseError:
    row_num: int
    row_data: Dict[str, Any]
    error_message: str


@dataclass
class ParseResult:
    leads: List[Lead]
    errors: List[ParseError]
    stats: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not self.stats:
            self.stats = {
                "total": len(self.leads) + len(self.errors),
                "processed": len(self.leads),
                "skipped": len(self.errors),
                "requires_review": sum(1 for lead in self.leads if lead.requires_review),
                "by_source": {},
            }
            for lead in self.leads:
                source = lead.source
                if source not in self.stats["by_source"]:
                    self.stats["by_source"][source] = 0
                self.stats["by_source"][source] += 1


class UnifiedParser:
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0

    def parse_file(self, file_path: str) -> ParseResult:
        file_path = file_path.strip('"')

        try:
            sep = "\t" if file_path.lower().endswith(".tsv") else ","
            df = pd.read_csv(file_path, sep=sep, dtype=str, keep_default_na=False)
        except Exception as e:
            raise ValueError(f"Failed to read file: {e}")

        headers = df.columns.tolist()
        return self._parse_dataframe(df, headers, file_path)

    def parse_raw_data(
        self,
        headers: List[str],
        rows: List[Dict[str, Any]],
        source_hint: Optional[str] = None,
    ) -> ParseResult:
        if not headers or not rows:
            return ParseResult(leads=[], errors=[], stats={"total": 0, "processed": 0, "skipped": 0, "requires_review": 0, "by_source": {}})

        df = pd.DataFrame(rows, columns=headers)
        return self._parse_dataframe(df, headers, source_hint or "raw_data")

    def _parse_dataframe(
        self,
        df: pd.DataFrame,
        headers: List[str],
        source_hint: str,
    ) -> ParseResult:
        is_file_path = source_hint.endswith((".csv", ".xlsx", ".xls")) if "." in source_hint else False
        source = detect_source(headers) if is_file_path or source_hint == "raw_data" else source_hint
        mapping, unmapped = map_columns(headers)

        if unmapped:
            print(f"[UnifiedParser] Unmapped columns: {unmapped}")

        leads: List[Lead] = []
        errors: List[ParseError] = []

        for idx, row_dict in df.iterrows():
            row_num = idx + 1
            try:
                lead = self._transform_row_to_lead(row_dict, mapping, source)
                leads.append(lead)
            except ValueError as e:
                errors.append(ParseError(row_num=row_num, row_data=dict(row_dict), error_message=str(e)))
            except Exception as e:
                errors.append(ParseError(row_num=row_num, row_data=dict(row_dict), error_message=f"Unexpected error: {e}"))

        return ParseResult(leads=leads, errors=errors)

    def _transform_row_to_lead(
        self,
        row: Dict[str, Any],
        mapping: Dict[str, str],
        source: str,
    ) -> Lead:
        import math
        transformed = transform_row(row, mapping, source)

        company = transformed.get("company")
        if company is None or (isinstance(company, str) and company.strip() == "") or (isinstance(company, float) and math.isnan(company)):
            raise ValueError(f"Missing required field 'company'")

        city = transformed.get("city") or ""
        state = transformed.get("state") or ""

        lead_dict = {
            "company": company,
            "city": city,
            "state": state,
            "name": transformed.get("name"),
            "email": transformed.get("email"),
            "property_address": transformed.get("property_address"),
            "phone": transformed.get("phone"),
            "website": transformed.get("website"),
            "source": source,
            "original_data": transformed.get("original_data", dict(row)),
        }

        lead = Lead(**lead_dict)

        if city and not lead.state:
            lead.state = "[MISSING_STATE]"
            lead.requires_review = True

        if lead.email and not lead.is_email_valid():
            lead.requires_review = True

        return lead

    def parse_google_sheet(
        self,
        sheet_url: str,
        sheet_name: Optional[str] = None,
        service_account_json: Optional[str] = None,
    ) -> ParseResult:
        import os

        if service_account_json:
            sa_path = service_account_json
        else:
            possible_paths = [
                os.path.join(os.getcwd(), "gtmengine-494418-9c53a5ae283d.json"),
                os.path.join(os.path.dirname(os.getcwd()), "gtmengine-494418-9c53a5ae283d.json"),
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    sa_path = p
                    break
            else:
                raise ValueError("Service account JSON not found")

        sheet_id = self._extract_sheet_id(sheet_url)
        if not sheet_id:
            raise ValueError(f"Invalid Google Sheets URL: {sheet_url}")

        try:
            import google.auth
            from googleapiclient.discovery import build
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(
                sa_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
            )
            service = build("sheets", "v4", credentials=credentials)

            spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            sheets = spreadsheet.get("sheets", [])
            target_sheet = sheet_name or sheets[0]["properties"]["title"] if sheets else "Sheet1"

            range_name = f"{target_sheet}!A1:ZZ"
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name,
            ).execute()
            values = result.get("values", [])

            if not values:
                return ParseResult(leads=[], errors=[], stats={"total": 0, "processed": 0, "skipped": 0, "requires_review": 0, "by_source": {}})

            headers = values[0]
            rows = values[1:]
            row_dicts = []
            for row in rows:
                row_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                row_dicts.append(row_dict)

            return self.parse_raw_data(headers, row_dicts, source_hint="Google Sheets")

        except ImportError:
            print("[UnifiedParser] google-api-python-client not installed. Attempting CSV export fallback.")
            return self._parse_sheet_csv_fallback(sheet_url, sheet_name)

    def _extract_sheet_id(self, url: str) -> Optional[str]:
        patterns = [
            r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
            r"key=([a-zA-Z0-9-_]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _parse_sheet_csv_fallback(self, sheet_url: str, sheet_name: Optional[str] = None) -> ParseResult:
        sheet_id = self._extract_sheet_id(sheet_url)
        if not sheet_id:
            raise ValueError(f"Invalid Google Sheets URL: {sheet_url}")

        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        if sheet_name:
            export_url += f"&gid={sheet_name}"

        try:
            df = pd.read_csv(export_url)
            headers = df.columns.tolist()
            return self._parse_dataframe(df, headers, "Google Sheets")
        except Exception as e:
            raise ValueError(f"Failed to fetch Google Sheet as CSV: {e}")