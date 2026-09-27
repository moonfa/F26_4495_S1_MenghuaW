from typing import Literal
from pydantic import BaseModel, Field


class ThreadAction(BaseModel):
    action: Literal[
        "continue",
        "update",
        "create",
        "deprioritize",
        "close",
        "ephemeral",
    ]
    thread_id: str | None = None
    title: str = Field(min_length=1, max_length=160)
    importance: Literal["high", "medium", "low"]
    importance_change: Literal[
        "new",
        "increased",
        "unchanged",
        "decreased",
    ]
    change_summary: str = Field(min_length=1, max_length=900)


class MasterResearchReport(BaseModel):
    """MVP AI output: one deep report plus minimal longitudinal metadata."""

    report_markdown: str = Field(min_length=1, max_length=30000)
    key_takeaways: list[str] = Field(default_factory=list, max_length=6)
    what_changed: str = Field(default="No previous review was available.", max_length=5000)
    thread_actions: list[ThreadAction] = Field(default_factory=list, max_length=8)


class EventImpact(BaseModel):
    thesis_area: str = Field(min_length=1, max_length=160)
    potential_impact: str = Field(min_length=1, max_length=1200)
    mechanism: str = Field(min_length=1, max_length=1400)
    evidence_refs: list[str] = Field(default_factory=list, max_length=8)
    confidence: Literal["high", "medium", "low"] = "medium"


class EventAnalysis(BaseModel):
    summary: str = Field(min_length=1, max_length=2500)
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
    impacts: list[EventImpact] = Field(default_factory=list, max_length=8)
    forecast_review_required: bool = False
    valuation_review_required: bool = False
    data_quality_notes: list[str] = Field(default_factory=list, max_length=10)
