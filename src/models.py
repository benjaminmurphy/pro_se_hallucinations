"""Data models for pro se complaint evaluation."""

from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field


class ComplaintCategory(str, Enum):
    """Categories of pro se complaints being evaluated."""

    LANDLORD_TENANT = "landlord_tenant"
    NEGLIGENCE = "negligence"
    CUSTODY_MODIFICATION = "custody_modification"


class Jurisdiction(str, Enum):
    """Court jurisdiction for the complaint."""

    MA_STATE = "ma_state"
    MA_FEDERAL = "ma_federal"


# Background information models for each category


class HousingBackgroundInformation(BaseModel):
    """Background information for landlord-tenant (quiet enjoyment) scenarios."""

    plaintiff_name: str = Field(..., description="Name of the plaintiff/tenant")
    defendant_name: str = Field(..., description="Name of the defendant/landlord")
    location: str = Field(
        ..., description="Address of the rental property involved in the dispute"
    )
    lease_start_date: str = Field(..., description="Lease start date")
    monthly_rent: str = Field(..., description="Monthly rent amount")
    estimated_damages: str = Field(..., description="Estimated monetary damages")
    venue: str = Field(..., description="Appropriate court venue for filing")


class NegligenceBackgroundInformation(BaseModel):
    """Background information for negligence/personal injury scenarios."""

    plaintiff_name: str = Field(..., description="Name of the injured plaintiff")
    defendant_name: str = Field(
        ..., description="Name of defendant (person or business responsible)"
    )
    incident_location: str = Field(
        ..., description="Address or location where the incident occurred"
    )
    incident_date: str = Field(..., description="Date of the incident")
    injury_description: str = Field(
        ..., description="Brief description of injuries sustained"
    )
    medical_expenses: str = Field(..., description="Estimated medical expenses")
    lost_wages: str = Field(..., description="Estimated lost wages")
    venue: str = Field(..., description="Appropriate court venue for filing")


class CustodyBackgroundInformation(BaseModel):
    """Background information for custody modification scenarios."""

    petitioner_name: str = Field(..., description="Name of parent seeking modification")
    respondent_name: str = Field(..., description="Name of other parent")
    child_names: str = Field(..., description="Names and ages of children involved")
    original_order_date: str = Field(
        ..., description="Date of original custody order"
    )
    current_arrangement: str = Field(
        ..., description="Brief summary of current custody arrangement"
    )
    venue: str = Field(
        ..., description="Probate and Family Court venue for filing"
    )


# Union type for all background info types
BackgroundInfo = Union[
    HousingBackgroundInformation,
    NegligenceBackgroundInformation,
    CustodyBackgroundInformation,
]


class Scenario(BaseModel):
    """A fact pattern used to generate a complaint."""

    id: str = Field(..., description="Unique identifier for this scenario")
    category: ComplaintCategory
    jurisdiction: Jurisdiction
    fact_pattern: str = Field(..., description="Detailed facts of the case")

    # Category-specific background info (only one should be populated)
    housing_background_info: Optional[HousingBackgroundInformation] = Field(
        None, description="Background info for landlord-tenant scenarios"
    )
    negligence_background_info: Optional[NegligenceBackgroundInformation] = Field(
        None, description="Background info for negligence scenarios"
    )
    custody_background_info: Optional[CustodyBackgroundInformation] = Field(
        None, description="Background info for custody modification scenarios"
    )


class Citation(BaseModel):
    """A legal citation extracted from a complaint."""

    raw_text: str = Field(
        ..., description="The citation as it appears in the complaint"
    )
    case_name: Optional[str] = Field(None, description="Extracted case name")
    volume: Optional[str] = Field(None, description="Reporter volume")
    reporter: Optional[str] = Field(None, description="Reporter abbreviation")
    page: Optional[str] = Field(None, description="Starting page number")
    year: Optional[int] = Field(None, description="Year of decision")
    court: Optional[str] = Field(None, description="Court that issued the decision")

    # Validation results
    is_valid: Optional[bool] = Field(None, description="Whether citation was validated")
    courtlistener_id: Optional[str] = Field(
        None, description="CourtListener cluster ID if found"
    )
    validation_error: Optional[str] = Field(
        None, description="Error message if validation failed"
    )
    opinion_text: Optional[str] = Field(
        None, description="Full opinion text from CourtListener for holding validation"
    )


class CauseOfAction(BaseModel):
    """A cause of action alleged in the complaint."""

    name: str = Field(..., description="Name of the cause of action")
    elements: list[str] = Field(default_factory=list, description="Required elements")
    elements_pled: dict[str, bool] = Field(
        default_factory=dict, description="Which elements were adequately pled"
    )
    states_claim: Optional[bool] = Field(
        None, description="Whether this cause of action properly states a claim"
    )
    reasoning: Optional[str] = Field(None, description="LLM judge reasoning")


class Complaint(BaseModel):
    """A generated legal complaint and its evaluation results."""

    id: str = Field(..., description="Unique identifier for this complaint")
    scenario_id: str = Field(..., description="ID of the source scenario")
    variation: Optional[str] = Field(None, description="Which variation was applied")

    # Generation metadata
    model: str = Field(..., description="LLM model used for generation")
    prompt: str = Field(..., description="Prompt used to generate the complaint")
    generation_timestamp: str = Field(..., description="ISO timestamp of generation")

    # The complaint itself
    text: str = Field(..., description="Full text of the generated complaint")


class EvaluationResult(BaseModel):
    """Aggregated results for a model's complaint generation."""

    model: str
    total_complaints: int = 0
    total_citations: int = 0
    valid_citations: int = 0
    hallucinated_citations: int = 0
    hallucination_rate: float = 0.0
    complaints_stating_claim: int = 0
    claim_success_rate: float = 0.0

    # Per-category breakdown
    by_category: dict[str, dict] = Field(default_factory=dict)
