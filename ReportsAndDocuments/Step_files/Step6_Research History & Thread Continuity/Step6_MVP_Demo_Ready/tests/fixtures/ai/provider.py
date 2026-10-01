import json
import os
import re
from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel


class AIProviderError(RuntimeError):
    def __init__(self, code: str, message: str, *, cause: Exception | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.cause = cause


@dataclass(frozen=True)
class AIProviderConfig:
    provider: str
    model: str


class BaseAIProvider:
    config: AIProviderConfig

    def analyze(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError


class MockAIProvider(BaseAIProvider):
    def __init__(self, model: str = "mock-model"):
        self.config = AIProviderConfig(provider="mock", model=model)

    def analyze(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel] | None = None,
    ) -> dict[str, Any]:
        context = json.loads(user_prompt.split("ANALYSIS_CONTEXT:\n", 1)[1])
        evidence = context.get("current_evidence") or {}
        company = evidence.get("company") or {}
        market = evidence.get("market") or {}
        valuation = evidence.get("valuation") or {}
        review_type = context.get("analysis_mode") or "initial"
        price = market.get("current_price")
        fwd_pe = valuation.get("forward_pe")
        symbol = company.get("symbol") or "Unknown"
        name = company.get("name") or symbol

        result = {
            "report_markdown": (
                f"# {name} ({symbol}) Master Research Report\n\n"
                f"## 1. Business Model & Earnings Logic\n"
                f"This is a development-mode report for {name}. The production Gemini provider "
                f"should replace this mock narrative with the full fundamental analysis.\n\n"
                f"## 2. Investment Classification\n"
                f"The company should be evaluated according to its economic model, growth profile, "
                f"and competitive structure.\n\n"
                f"## 3. Moat & Competitive Position\n"
                f"A production review should identify the specific mechanisms supporting durable advantage.\n\n"
                f"## 4. Financial Quality\n"
                f"Current price: {price if price is not None else 'N/A'}. "
                f"Forward P/E: {fwd_pe if fwd_pe is not None else 'N/A'}.\n\n"
                f"## 5. Valuation Context\n"
                f"Valuation should be interpreted against the company's growth and margin expectations.\n\n"
                f"## 6. Key Growth Drivers\n"
                f"Production mode should identify the few drivers that matter most now.\n\n"
                f"## 7. Catalysts\nProduction mode should identify observable milestones.\n\n"
                f"## 8. Key Risks\nProduction mode should focus on causal risk mechanisms.\n\n"
                f"## 9. What Changed Since the Last Review\n"
                f"Review mode: {review_type}.\n\n"
                f"## 10. What Matters Most Now\n"
                f"This section is a development placeholder.\n\n"
                f"## 11. What to Monitor\n"
                f"Monitor the key operating and valuation variables supplied by the Evidence Snapshot."
            ),
            "key_takeaways": [
                "Mock mode is active; use Gemini for the production research report.",
                f"Current review mode: {review_type}.",
            ],
            "what_changed": "Mock provider does not interpret evidence deltas.",
            "thread_actions": [],
        }
        return _validate_or_return(result, response_schema)


class GeminiProvider(BaseAIProvider):
    def __init__(self, model: str):
        self.config = AIProviderConfig(provider="gemini", model=model)
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise AIProviderError(
                "gemini_sdk_not_installed",
                "Install google-genai with 'pip install -U google-genai'.",
                cause=exc,
            ) from exc
        self._types = types
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise AIProviderError("missing_ai_credentials", "GEMINI_API_KEY is not configured.")
        self.client = genai.Client(api_key=api_key)

    def analyze(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel] | None = None,
    ) -> dict[str, Any]:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        try:
            config_kwargs: dict[str, Any] = {
                "response_mime_type": "application/json",
                "temperature": 0.35,
                "max_output_tokens": 6000,
            }
            if response_schema is not None:
                config_kwargs["response_schema"] = response_schema

            config = self._types.GenerateContentConfig(**config_kwargs)
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=full_prompt,
                config=config,
            )

            parsed = getattr(response, "parsed", None)
            if isinstance(parsed, BaseModel):
                return parsed.model_dump(mode="json")

            text = getattr(response, "text", None)
            if not text:
                raise AIProviderError("empty_ai_response", "Gemini returned no text output.")
            return _parse_json(text)
        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError("ai_provider_error", str(exc)[:500], cause=exc) from exc


def _validate_or_return(result: dict[str, Any], response_schema: type[BaseModel] | None) -> dict[str, Any]:
    if response_schema is None:
        return result
    try:
        return response_schema.model_validate(result).model_dump(mode="json")
    except Exception as exc:
        raise AIProviderError("mock_schema_validation_error", str(exc)[:500], cause=exc) from exc


def _parse_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AIProviderError("invalid_json_output", f"AI output was not valid JSON: {exc}", cause=exc) from exc
    if not isinstance(value, dict):
        raise AIProviderError("invalid_json_shape", "AI output must be a JSON object.")
    return value


def build_ai_provider() -> BaseAIProvider:
    provider = os.getenv("AI_PROVIDER", "mock").strip().lower()
    model = os.getenv("AI_MODEL", "gemini-3.8-flash").strip()
    if provider == "mock":
        return MockAIProvider()
    if provider in {"gemini", "google"}:
        return GeminiProvider(model=model)
    raise AIProviderError("unsupported_ai_provider", f"Unsupported AI_PROVIDER: {provider}")
