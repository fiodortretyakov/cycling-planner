from __future__ import annotations

from pydantic import BaseModel


class VisaRequest(BaseModel):
    citizenship: str
    destinations: list[str]


class VisaResult(BaseModel):
    requires_visa: bool
    notes: str


def check_visa_requirements(request: VisaRequest) -> VisaResult:
    # Mock: assume Schengen travel for EU passport needs no visa
    if request.citizenship.lower() in {"netherlands", "germany", "denmark", "france", "spain", "italy"}:
        return VisaResult(requires_visa=False, notes="Schengen area travel — no visa required for short stays")
    return VisaResult(requires_visa=True, notes="Check embassy sites; mock result indicates potential visa requirement")
