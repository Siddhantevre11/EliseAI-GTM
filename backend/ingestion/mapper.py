from typing import List, Dict, Optional, Any


COLUMN_ALIASES: Dict[str, List[str]] = {
    "company": [
        "company",
        "account name",
        "organization name",
        "firm",
        "organization",
        "company name",
        "account",
        "company_name",
        "companyname",
        "account_name",
        "organization_name",
        "org name",
        "org_name",
    ],
    "city": [
        "city",
        "billing city",
        "location",
        "town",
        "municipality",
        "city name",
        "city_name",
    ],
    "state": [
        "state",
        "billing state",
        "state code",
        "province",
        "state/province",
        "state_code",
        "stateprovince",
        "region",
    ],
    "name": [
        "name",
        "contact name",
        "full name",
        "contact",
        "person",
        "full_name",
        "contact_name",
        "first name",
        "last name",
        "full name",
    ],
    "email": [
        "email",
        "email address",
        "contact email",
        "e-mail",
        "email_address",
        "emailaddress",
        "contact email address",
        "work email",
        "mail",
    ],
    "property_address": [
        "property address",
        "address",
        "street address",
        "street",
        "address line 1",
        "address1",
        "address_line_1",
        "addr",
        "location address",
    ],
    "phone": [
        "phone",
        "phone number",
        "telephone",
        "mobile",
        "cell",
        "phone_number",
        "phonenumber",
        "contact number",
        "tel",
        "mobile phone",
    ],
    "website": [
        "website",
        "web site",
        "url",
        "company website",
        "website url",
        "company url",
        "web",
        "site",
    ],
}


SOURCE_SIGNATURES: Dict[str, List[str]] = {
    "Salesforce": ["account_name", "billing_city", "billing_state", "account_id", "sfdc"],
    "HubSpot": ["company_id", "contact_id", "hubspot", "hs_", "hubspot_contact", "hubspot_id"],
    "Apollo": ["organization_name", "apollo_id", "apollo_contact", "linkedin_url"],
    "LinkedIn": ["linkedin_profile", "linkedin_url", "profile_url"],
    "Generic CSV": [],
}


def normalize_header(header: str) -> str:
    if not header:
        return ""
    return header.strip().lower().replace(" ", "_").replace("-", "_")


def detect_source(headers: List[str]) -> str:
    normalized_headers = [normalize_header(h) for h in headers]
    header_set = set(normalized_headers)

    source_priority = ["Salesforce", "HubSpot", "Apollo", "LinkedIn"]

    for source in source_priority:
        signatures = SOURCE_SIGNATURES.get(source, [])
        for sig in signatures:
            if sig.lower() in header_set:
                return source

    return "Generic CSV"


def find_standard_field(header: str) -> Optional[str]:
    if not header or not header.strip():
        return None
    
    normalized = normalize_header(header)

    for standard_field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if normalize_header(alias) == normalized:
                return standard_field
            if alias.lower() in normalized or normalized in alias.lower():
                return standard_field

    return None


def map_columns(headers: List[str]) -> tuple:
    mapping: Dict[str, str] = {}
    unmapped: List[str] = []

    for header in headers:
        standard_field = find_standard_field(header)
        if standard_field:
            if standard_field not in mapping:
                mapping[header] = standard_field
            else:
                unmapped.append(header)
        else:
            unmapped.append(header)

    return mapping, unmapped


def detect_source(headers: List[str]) -> str:
    normalized_headers = [normalize_header(h) for h in headers if h and h.strip()]
    header_set = set(normalized_headers)
    header_str = " ".join(normalized_headers).lower()

    source_priority = ["Salesforce", "HubSpot", "LinkedIn", "Apollo"]

    for source in source_priority:
        signatures = SOURCE_SIGNATURES.get(source, [])
        for sig in signatures:
            sig_normalized = normalize_header(sig)
            if sig_normalized in header_set or sig_normalized in header_str:
                return source

    return "Generic CSV"


def transform_row(
    row: Dict[str, Any],
    mapping: Dict[str, str],
    source: str,
) -> Dict[str, Any]:
    transformed: Dict[str, Any] = {
        "source": source,
        "original_data": dict(row),
    }

    for raw_header, standard_field in mapping.items():
        if raw_header in row:
            value = row[raw_header]
            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    value = None
            transformed[standard_field] = value

    return transformed