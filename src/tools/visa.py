from __future__ import annotations

from pydantic import BaseModel


class VisaRequest(BaseModel):
    citizenship: str
    destinations: list[str]


class VisaResult(BaseModel):
    requires_visa: bool
    notes: str


# Comprehensive visa-free travel data for common scenarios
# EU/Schengen countries
SCHENGEN_COUNTRIES = {
    "austria", "belgium", "czechia", "czech republic", "denmark", "estonia", "finland",
    "france", "germany", "greece", "hungary", "iceland", "italy", "latvia", "liechtenstein",
    "lithuania", "luxembourg", "malta", "netherlands", "norway", "poland", "portugal",
    "slovakia", "slovenia", "spain", "sweden", "switzerland"
}

# Countries with visa-free access to Schengen for tourism (up to 90 days)
VISA_FREE_TO_SCHENGEN = {
    "usa", "united states", "canada", "australia", "new zealand", "japan", "south korea",
    "singapore", "united kingdom", "uk", "britain", "ireland", "mexico", "brazil",
    "argentina", "chile", "israel", "uae", "united arab emirates"
}

# EU countries not in Schengen
EU_NON_SCHENGEN = {"ireland", "bulgaria", "romania", "croatia", "cyprus"}


def check_visa_requirements(request: VisaRequest) -> VisaResult:
    """
    Check visa requirements based on citizenship and destinations.
    Uses static visa policy data for common travel scenarios.
    """
    citizenship = request.citizenship.lower().strip()
    destinations = [d.lower().strip() for d in request.destinations]
    
    # Check if all destinations are in Schengen area
    all_schengen = all(dest in SCHENGEN_COUNTRIES for dest in destinations)
    
    # Case 1: EU/Schengen citizen traveling within Schengen
    if citizenship in SCHENGEN_COUNTRIES and all_schengen:
        return VisaResult(
            requires_visa=False,
            notes="Schengen area travel — no visa required. EU/EEA citizens have freedom of movement."
        )
    
    # Case 2: EU citizen traveling within EU (including non-Schengen EU)
    all_eu = all(dest in SCHENGEN_COUNTRIES or dest in EU_NON_SCHENGEN for dest in destinations)
    if citizenship in SCHENGEN_COUNTRIES and all_eu:
        return VisaResult(
            requires_visa=False,
            notes="EU travel — no visa required. Freedom of movement applies."
        )
    
    # Case 3: Visa-free country traveling to Schengen
    if citizenship in VISA_FREE_TO_SCHENGEN and all_schengen:
        return VisaResult(
            requires_visa=False,
            notes=f"Visa-free travel to Schengen area for {request.citizenship} citizens. "
                  "Up to 90 days in any 180-day period. Valid passport required."
        )
    
    # Case 4: UK/Ireland special cases
    if citizenship in {"united kingdom", "uk", "britain"}:
        return VisaResult(
            requires_visa=False,
            notes="UK citizens can travel visa-free to Schengen for up to 90 days. "
                  "Check individual country requirements for longer stays."
        )
    
    # Case 5: Within same country (domestic travel)
    if len(destinations) == 1 and destinations[0] == citizenship:
        return VisaResult(
            requires_visa=False,
            notes="Domestic travel — no visa required."
        )
    
    # Default: May require visa (recommend checking)
    dest_list = ", ".join([d.title() for d in destinations])
    return VisaResult(
        requires_visa=True,
        notes=f"Visa may be required for {request.citizenship.title()} citizens traveling to {dest_list}. "
              "Please check with the relevant embassies or consulates. "
              "Visit official government travel advisory websites for accurate requirements."
    )
