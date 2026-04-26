from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator
from dataclasses import dataclass, field


STATE_MAP: Dict[str, str] = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
    "district of columbia": "DC",
    "puerto rico": "PR",
}


@dataclass
class ValidationResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    failed_fields: List[str] = field(default_factory=list)
    quality_score: float = 100.0

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, field: str, message: str):
        self.errors.append(f"{field}: {message}")
        if field not in self.failed_fields:
            self.failed_fields.append(field)
        self.quality_score -= 20

    def add_warning(self, message: str):
        self.warnings.append(message)
        self.quality_score -= 5

    def __bool__(self) -> bool:
        return self.is_valid


class Lead(BaseModel):
    company: str
    city: str
    state: str
    name: Optional[str] = None
    email: Optional[str] = None
    property_address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    source: str = "unknown"
    original_data: Dict[str, Any] = Field(default_factory=dict)
    requires_review: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"extra": "allow"}

    @field_validator("state", mode="before")
    @classmethod
    def coerce_state(cls, v: Any) -> str:
        if v is None or v == "":
            return "[MISSING_STATE]"

        if isinstance(v, str):
            v = v.strip().lower()
            if len(v) == 2:
                return v.upper()
            if v in STATE_MAP:
                return STATE_MAP[v]
            return "[MISSING_STATE]"

        return "[MISSING_STATE]"

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: Any) -> Optional[str]:
        if v is None or v == "":
            return None

        if isinstance(v, str):
            v = v.strip()
            if "@" not in v or "." not in v.split("@")[-1]:
                return v
            return v.lower()

        return None

    def is_email_valid(self) -> bool:
        if not self.email:
            return True
        return "@" in self.email and "." in self.email.split("@")[-1]

    @model_validator(mode="after")
    def set_review_flag(self) -> "Lead":
        if self.state == "[MISSING_STATE]":
            self.requires_review = True
        if self.email and not self.is_email_valid():
            self.requires_review = True
        return self