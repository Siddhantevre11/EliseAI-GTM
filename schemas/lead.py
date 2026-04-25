"""
schemas/lead.py — Pydantic models for EliseAI GTM

Defines input/output schemas with validation.
"""

import re
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator


EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
}


class LeadInput(BaseModel):
    """Input schema for lead enrichment."""
    
    # Required fields (pipeline needs these)
    company: str = Field(..., min_length=1, description="Company name")
    city: str = Field(..., min_length=1, description="City")
    state: str = Field(..., min_length=2, max_length=2, description="State (2-letter)")
    
    # Optional fields
    name: Optional[str] = Field(None, description="Contact name")
    email: Optional[str] = Field(None, description="Email address")
    property_address: Optional[str] = Field(None, description="Property address")
    phone: Optional[str] = Field(None, description="Phone number")
    zip: Optional[str] = Field(None, description="ZIP code")
    
    # Metadata
    source: str = Field("api", description="Input source (csv/sheet/api)")
    original_data: dict = Field(default_factory=dict, description="Original input for mapping")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not re.match(EMAIL_REGEX, v):
            raise ValueError(f"Invalid email format: {v}")
        return v
    
    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in US_STATES:
            raise ValueError(f"Invalid state code: {v}. Must be 2-letter US state.")
        return v
    
    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return "".join(c for c in v if c.isdigit())


class LeadOutput(BaseModel):
    """Output schema for enrichment result."""
    
    tier: Optional[str] = None
    priority_score: Optional[int] = None
    score_rationale: Optional[str] = None
    key_data_points: dict = {}
    sales_signal: Optional[str] = None
    talking_points: List[str] = []
    email_draft: Optional[dict] = None
    buying_signals: Optional[dict] = None
    objection_handling: Optional[dict] = None
    peer_case_study: Optional[dict] = None
    roi_estimate: Optional[dict] = None
    decision_maker_context: Optional[dict] = None
    industry_benchmark: Optional[dict] = None
    
    # Metadata fields
    _lead: Optional[dict] = None
    _raw_data: Optional[dict] = None
    _api_errors: List[str] = []
    _needs_manual_review: bool = False
    _validation: Optional[dict] = None


class ValidationResult(BaseModel):
    """Validation result for a lead."""
    
    is_valid: bool = True
    errors: List[str] = []
    warnings: List[str] = []
    failed_fields: List[str] = []
    quality_score: int = 100
    
    def add_error(self, field: str, message: str):
        self.is_valid = False
        self.errors.append(f"{field}: {message}")
        if field not in self.failed_fields:
            self.failed_fields.append(field)
        self.quality_score = max(0, self.quality_score - 25)
    
    def add_warning(self, message: str):
        self.warnings.append(message)
        self.quality_score = max(0, self.quality_score - 10)