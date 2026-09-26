from typing import Literal
from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


Confidence = Literal["high", "medium", "low"]

InsightBasis = Literal[
    "evidence",
    "background_knowledge",
    "combined",
]


class ResearchInsight(BaseModel):
    """
    A structured investment-research insight.

    The purpose is to force the model to explain:
    observation -> mechanism -> financial implication
    -> monitoring signal -> invalidation signal.
    """

    title: str = Field(
        min_length=1,
        max_length=160,
    )

    observation: str = Field(
        min_length=1,
        max_length=1200,
        description=(
            "What the supplied evidence or stable business knowledge shows."
        ),
    )

    mechanism: str = Field(
        min_length=1,
        max_length=1800,
        description=(
            "Why this matters and how the business/economic mechanism works."
        ),
    )

    financial_implication: str = Field(
        min_length=1,
        max_length=1400,
        description=(
            "Potential implication for revenue, margins, earnings, cash flow, "
            "capital efficiency, or competitive position."
        ),
    )

    what_to_monitor: list[str] = Field(
        default_factory=list,
        max_length=5,
    )

    invalidation_signal: str | None = Field(
        default=None,
        max_length=900,
    )

    evidence_refs: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    basis: InsightBasis = "combined"

    confidence: Confidence = "medium"


class ResearchNode(BaseModel):
    """
    A future research object that can be tracked over time.
    """

    node_type: Literal[
        "sub_thesis",
        "driver",
        "kpi",
        "risk",
        "valuation_question",
    ]

    title: str = Field(
        min_length=1,
        max_length=160,
    )

    research_question: str = Field(
        min_length=1,
        max_length=600,
    )

    rationale: str = Field(
        min_length=1,
        max_length=1400,
    )

    evidence_refs: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    confidence: Confidence = "medium"


class CompanyProfileAnalysis(BaseModel):
    """
    Structured output for the main company research analysis.
    """

    summary: str = Field(
        min_length=1,
        max_length=3500,
    )

    business_model: str = Field(
        min_length=1,
        max_length=4000,
    )

    investment_classification: list[str] = Field(
        default_factory=list,
        max_length=8,
    )

    financial_quality: str = Field(
        min_length=1,
        max_length=3500,
    )

    valuation_context: str = Field(
        min_length=1,
        max_length=3500,
    )

    moat_assessment: str = Field(
        min_length=1,
        max_length=3500,
    )

    competitive_position: str = Field(
        min_length=1,
        max_length=3500,
    )

    key_insights: list[ResearchInsight] = Field(
        default_factory=list,
        max_length=6,
    )

    key_drivers: list[ResearchInsight] = Field(
        default_factory=list,
        max_length=6,
    )

    key_risks: list[ResearchInsight] = Field(
        default_factory=list,
        max_length=6,
    )

    recent_news_signals: list[ResearchInsight] = Field(
        default_factory=list,
        max_length=6,
    )

    monitoring_kpis: list[str] = Field(
        default_factory=list,
        max_length=12,
    )

    research_nodes: list[ResearchNode] = Field(
        default_factory=list,
        max_length=10,
    )

    evidence_gaps: list[str] = Field(
        default_factory=list,
        max_length=12,
    )

    confidence: Confidence = "medium"


class EventImpact(BaseModel):
    thesis_area: str = Field(
        min_length=1,
        max_length=160,
    )

    potential_impact: str = Field(
        min_length=1,
        max_length=1200,
    )

    mechanism: str = Field(
        min_length=1,
        max_length=1400,
    )

    evidence_refs: list[str] = Field(
        default_factory=list,
        max_length=8,
    )

    confidence: Confidence = "medium"


class EventAnalysis(BaseModel):
    summary: str = Field(
        min_length=1,
        max_length=2500,
    )

    event_type: Literal[
        "earnings",
        "guidance",
        "product",
        "regulatory",
        "management",
        "capital_allocation",
        "partnership",
        "acquisition",
        "macro",
        "other",
    ] = "other"

    impacts: list[EventImpact] = Field(
        default_factory=list,
        max_length=8,
    )

    forecast_review_required: bool = False

    valuation_review_required: bool = False

    data_quality_notes: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

class AnalysisDraftResponse(BaseModel):
    draft_id: int
    snapshot_id: int
    analysis_type: str
    status: str
    provider: str
    model: str
    prompt_version: str
    input_hash: str
    result: Optional[Any] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class SyncRequest(BaseModel):
    ticker: str

class AnalysisRequest(BaseModel):
    analysis_type: str
    force_refresh: bool = False

class EvidenceSyncResponse(BaseModel):
    snapshot_id: int
    ticker: str
    provider: str
    operation: str
    status: str
    requested_at: datetime
    retrieved_at: Optional[datetime] = None
    source_url: Optional[str] = None
    data: Optional[Any] = None
    warnings: Optional[list] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class EvidenceHistoryItem(BaseModel):
    snapshot_id: int
    ticker: str
    operation: str
    status: str
    provider: str
    requested_at: datetime
    retrieved_at: Optional[datetime] = None
    data: Optional[Any] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class AnalysisDraftResponse(BaseModel):
    draft_id: int
    snapshot_id: int
    analysis_type: str
    status: str
    provider: str
    model: str
    prompt_version: str
    input_hash: str
    result: Optional[Any] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None