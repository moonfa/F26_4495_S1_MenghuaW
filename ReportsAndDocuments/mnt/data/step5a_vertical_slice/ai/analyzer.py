from typing import Any
import hashlib
import json

from .prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_company_prompt
from .provider import BaseAIProvider, AIProviderError
from .schemas import EventAnalysis, MasterResearchReport


class AIAnalyzer:
    def __init__(self, provider: BaseAIProvider):
        self.provider = provider

    @staticmethod
    def input_hash(
        *,
        evidence: dict[str, Any],
        review_context: dict[str, Any],
        previous_key_takeaways: list[str],
        prompt_version: str = PROMPT_VERSION,
    ) -> str:
        value = json.dumps(
            {
                "prompt_version": prompt_version,
                "evidence": evidence,
                "review_context": review_context,
                "previous_key_takeaways": previous_key_takeaways,
            },
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(value).hexdigest()

    def analyze_company(
        self,
        *,
        evidence: dict[str, Any],
        review_context: dict[str, Any],
        previous_key_takeaways: list[str],
        thread_context: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        prompt = build_company_prompt(
            evidence=evidence,
            review_context=review_context,
            previous_key_takeaways=previous_key_takeaways,
            thread_context=thread_context,
        )
        result = self.provider.analyze(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
            response_schema=MasterResearchReport,
        )
        return MasterResearchReport.model_validate(result).model_dump(mode="json")

    def analyze_event(self, *, evidence: dict[str, Any]) -> dict[str, Any]:
        raise AIProviderError(
            "event_analysis_not_enabled_in_step5a",
            "Step 5A focuses on the Master Research Report. Event analysis is unchanged for later integration.",
        )
