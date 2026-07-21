from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

OrgSize = Literal["1-10", "11-50", "51-200", "200+"]


class QuestionnaireResponses(BaseModel):
    """
    Raw answers to the readiness questionnaire.
    Score is 0-5 per question (0 = not present/no, 5 = fully mature/yes).
    """

    model_config = ConfigDict(extra="forbid")

    # Data readiness
    data_centralized: int = Field(ge=0, le=5, description="Is data centralized and accessible?")
    data_quality_process: int = Field(ge=0, le=5, description="Is there a data quality process?")

    # Talent
    ai_literate_staff: int = Field(ge=0, le=5, description="Staff AI literacy level")
    dedicated_owner: int = Field(ge=0, le=5, description="Is there a named AI/automation owner?")

    # Governance
    has_ai_policy: int = Field(ge=0, le=5, description="Existing AI usage/governance policy")
    risk_review_process: int = Field(ge=0, le=5, description="Formal risk review before deployment")

    # Infrastructure
    cloud_or_api_access: int = Field(ge=0, le=5, description="Access to cloud/API infrastructure")
    integration_capacity: int = Field(ge=0, le=5, description="Ability to integrate AI into existing systems")

    # Leadership
    leadership_buy_in: int = Field(ge=0, le=5, description="Leadership support for AI adoption")
    budget_allocated: int = Field(ge=0, le=5, description="Budget allocated for AI initiatives")


class AssessmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    org_name: str = Field(min_length=1, max_length=200)
    sector: str = Field(min_length=1, max_length=100)
    org_size: OrgSize
    responses: QuestionnaireResponses


class CategoryScore(BaseModel):
    category: str
    score: float
    max_score: float


class AssessmentResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_name: str
    sector: str
    org_size: str
    category_scores: dict
    overall_score: float
    readiness_tier: str
    created_at: datetime
