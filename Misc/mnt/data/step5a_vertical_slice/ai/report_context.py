from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReviewContext:
    review_type: str
    material_change: bool
    current_snapshot_id: int
    previous_snapshot_id: int | None
    previous_report_id: int | None
    previous_key_takeaways: list[str]
    evidence_delta: dict[str, Any]


def build_evidence_delta(
    current: dict[str, Any],
    previous: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compact deterministic comparison. No AI interpretation."""
    if not previous:
        return {
            "status": "initial",
            "changed_sections": [],
            "metric_changes": [],
            "new_news_count": len(current.get("recent_news") or []),
        }

    changes: list[dict[str, Any]] = []

    for section, fields in {
        "market": [
            "current_price",
            "market_cap",
            "year_high",
            "year_low",
            "beta",
        ],
        "valuation": [
            "pe_ttm",
            "forward_pe",
            "peg",
            "price_to_sales",
            "price_to_book",
            "price_to_free_cash_flow",
            "ev_to_ebitda",
            "free_cash_flow_yield",
        ],
        "financial_health": [
            "revenue_growth",
            "earnings_growth",
            "eps_growth",
            "gross_margin",
            "operating_margin",
            "profit_margin",
            "return_on_equity",
            "return_on_invested_capital",
            "debt_to_equity",
        ],
        "analyst_consensus": [
            "target_consensus",
            "target_high",
            "target_low",
            "total_analysts",
        ],
    }.items():
        current_section = current.get(section) or {}
        previous_section = previous.get(section) or {}
        for field in fields:
            new = current_section.get(field)
            old = previous_section.get(field)
            if new == old or (new is None and old is None):
                continue
            changes.append(
                {
                    "section": section,
                    "field": field,
                    "previous": old,
                    "current": new,
                }
            )

    previous_news = previous.get("recent_news") or []
    current_news = current.get("recent_news") or []
    previous_titles = {
        item.get("title")
        for item in previous_news
        if isinstance(item, dict) and item.get("title")
    }
    new_news = [
        item for item in current_news
        if isinstance(item, dict)
        and item.get("title")
        and item.get("title") not in previous_titles
    ]

    current_missing = set(
        (current.get("data_quality") or {}).get("sections_missing") or []
    )
    previous_missing = set(
        (previous.get("data_quality") or {}).get("sections_missing") or []
    )

    restored = sorted(previous_missing - current_missing)
    newly_missing = sorted(current_missing - previous_missing)

    changed_sections = sorted(
        {
            item["section"]
            for item in changes
        }
        | ({"recent_news"} if new_news else set())
        | ({"data_quality"} if restored or newly_missing else set())
    )

    # Materiality is deliberately conservative and deterministic.
    material = bool(changes or new_news or restored or newly_missing)
    return {
        "status": "changed" if material else "unchanged",
        "changed_sections": changed_sections,
        "metric_changes": changes[:30],
        "new_news_count": len(new_news),
        "restored_sections": restored,
        "newly_missing_sections": newly_missing,
    }


def build_review_context(
    *,
    current_snapshot_id: int,
    current_evidence: dict[str, Any],
    previous_snapshot_id: int | None,
    previous_report_id: int | None,
    previous_evidence: dict[str, Any] | None,
    previous_key_takeaways: list[str],
) -> ReviewContext:
    delta = build_evidence_delta(
        current_evidence,
        previous_evidence,
    )
    material = delta.get("status") == "changed"
    if previous_snapshot_id is None:
        review_type = "initial"
    elif material:
        review_type = "full_follow_up"
    else:
        review_type = "low_change"

    return ReviewContext(
        review_type=review_type,
        material_change=material,
        current_snapshot_id=current_snapshot_id,
        previous_snapshot_id=previous_snapshot_id,
        previous_report_id=previous_report_id,
        previous_key_takeaways=previous_key_takeaways[:6],
        evidence_delta=delta,
    )
