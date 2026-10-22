import asyncio
from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from app.config import settings
from app.main import app
from app.models.natural_language import ParsedInvestmentIntent
from app.services import natural_language_recommendation as recommendation_module
from app.services.natural_language_recommendation import (
    NaturalLanguageRecommendationService,
    NaturalLanguageServiceError,
)

client = TestClient(app)


def test_filters_universe_with_strict_exclusions() -> None:
    instruments = [
        {
            "ticker": "GOOD",
            "name": "Good ETF",
            "sleeve": "us_equity",
            "region": "us",
            "category": "Large Blend",
            "expense_ratio_pct": 0.1,
            "distribution_yield_pct": 2.0,
            "sharia_compliant": True,
            "esg": True,
            "crypto": False,
        },
        {
            "ticker": "CRYPTO",
            "name": "Crypto ETF",
            "sleeve": "us_equity",
            "region": "us",
            "category": "Large Blend",
            "expense_ratio_pct": 0.1,
            "distribution_yield_pct": 2.0,
            "sharia_compliant": True,
            "esg": True,
            "crypto": True,
        },
        {
            "ticker": "UNKNOWN",
            "name": "Unknown flags ETF",
            "sleeve": "us_equity",
            "region": "us",
            "category": "Large Blend",
            "expense_ratio_pct": 0.1,
            "distribution_yield_pct": 2.0,
            "sharia_compliant": True,
            "esg": True,
        },
    ]
    service = NaturalLanguageRecommendationService(instruments)
    intent = ParsedInvestmentIntent(
        preferred_sleeves=["us_equity"],
        preferred_categories=["Large Blend"],
        preferred_regions=["us"],
        max_expense_ratio_pct=0.2,
        min_distribution_yield_pct=1.5,
        exclude_crypto=True,
        require_esg=True,
        require_sharia_compliant=True,
    )

    matches = service.filter_instruments(intent)

    assert [instrument.ticker for instrument in matches] == ["GOOD"]
    assert "explicitly marked as non-crypto" in matches[0].justification
    assert "marked ESG" in matches[0].justification
    assert "marked Sharia compliant" in matches[0].justification


def test_intent_rejects_filter_values_not_in_universe() -> None:
    service = NaturalLanguageRecommendationService(
        [{"sleeve": "us_equity", "category": "Large Blend", "region": "us"}]
    )

    with pytest.raises(NaturalLanguageServiceError) as error:
        service._parse_intent('{"preferred_sleeves":["invented"],'
                              '"preferred_categories":[],"preferred_regions":[]}')
    assert error.value.status_code == 502
    assert "unknown sleeve" in str(error.value)


def test_parse_intent_uses_gemini_json_schema(monkeypatch) -> None:
    service = NaturalLanguageRecommendationService(
        [{"sleeve": "us_equity", "category": "Large Blend", "region": "us"}]
    )
    captured: dict[str, object] = {}

    async def fake_generate(**kwargs):
        captured.update(kwargs)
        return (
            '{"preferred_sleeves":["us_equity"],'
            '"preferred_categories":["Large Blend"],'
            '"preferred_regions":["us"],'
            '"max_expense_ratio_pct":0.2,'
            '"min_distribution_yield_pct":null,'
            '"exclude_crypto":true,"require_esg":false,'
            '"require_sharia_compliant":false}'
        )

    monkeypatch.setattr(service, "_generate", fake_generate)

    intent = asyncio.run(service.parse_intent("low-cost US equity"))

    assert intent.preferred_sleeves == ["us_equity"]
    schema = captured["response_schema"]
    assert schema["properties"]["preferred_sleeves"]["items"]["enum"] == [
        "us_equity"
    ]
    assert schema["properties"]["preferred_categories"]["items"]["enum"] == [
        "Large Blend"
    ]
    assert schema["properties"]["preferred_sleeves"]["type"] == "ARRAY"
    assert schema["properties"]["preferred_sleeves"]["items"]["type"] == "STRING"
    assert "additionalProperties" not in schema
    assert "maxItems" not in schema["properties"]["preferred_sleeves"]
    assert "anyOf" not in schema["properties"]["max_expense_ratio_pct"]


def test_generate_uses_async_gemini_json_schema(monkeypatch) -> None:
    calls: dict[str, object] = {}

    class FakeModels:
        async def generate_content(self, **kwargs):
            calls["request"] = kwargs
            return SimpleNamespace(text='{"preferred_sleeves":[]}')

    class FakeAsyncClient:
        def __init__(self):
            self.models = FakeModels()

        async def aclose(self):
            calls["closed"] = True

    class FakeClient:
        def __init__(self, **kwargs):
            calls["client_options"] = kwargs
            self.aio = FakeAsyncClient()

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(recommendation_module.genai, "Client", FakeClient)
    service = NaturalLanguageRecommendationService([])

    result = asyncio.run(
        service._generate(
            contents="test prompt",
            system_instruction="system",
            response_schema={"type": "OBJECT"},
        )
    )

    assert result == '{"preferred_sleeves":[]}'
    assert calls["request"]["model"] == settings.LLM_MODEL
    assert calls["request"]["config"].response_mime_type == "application/json"
    assert calls["request"]["config"].response_json_schema == {"type": "OBJECT"}
    assert calls["closed"] is True


def test_generate_reports_missing_gemini_key(monkeypatch) -> None:
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    service = NaturalLanguageRecommendationService([])

    with pytest.raises(NaturalLanguageServiceError) as error:
        asyncio.run(
            service._generate(
                contents="test prompt",
                system_instruction="system",
            )
        )

    assert error.value.status_code == 503


def test_generate_logs_provider_error_code_and_message_without_api_key(
    monkeypatch, caplog
) -> None:
    api_key = "test-api-key"

    class FakeModels:
        async def generate_content(self, **kwargs):
            raise recommendation_module.genai_errors.ClientError(
                400,
                {
                    "error": {
                        "code": 400,
                        "status": "INVALID_ARGUMENT",
                        "message": f"Request rejected for {api_key}",
                    }
                },
            )

    class FakeAsyncClient:
        models = FakeModels()

        async def aclose(self):
            return None

    class FakeClient:
        def __init__(self, **kwargs):
            self.aio = FakeAsyncClient()

    monkeypatch.setattr(settings, "GEMINI_API_KEY", api_key)
    monkeypatch.setattr(recommendation_module.genai, "Client", FakeClient)
    service = NaturalLanguageRecommendationService([])

    with pytest.raises(NaturalLanguageServiceError) as error:
        asyncio.run(
            service._generate(
                contents="test prompt",
                system_instruction="system",
                operation="intent parsing",
            )
        )

    assert error.value.status_code == 502
    assert "http_code=400" in caplog.text
    assert "provider_status=INVALID_ARGUMENT" in caplog.text
    assert "[redacted]" in caplog.text
    assert api_key not in caplog.text


def test_natural_language_endpoint_returns_dataset_matches(monkeypatch) -> None:
    intent = ParsedInvestmentIntent(
        preferred_sleeves=["cash"],
        exclude_crypto=True,
    )

    async def fake_parse_intent(self, prompt):
        return intent

    async def fake_explain_matches(self, prompt, parsed_intent, matches):
        assert prompt == "Find cash ETFs without crypto."
        assert all(match.crypto is False for match in matches)
        return "These instruments match the requested cash sleeve."

    monkeypatch.setattr(
        NaturalLanguageRecommendationService, "parse_intent", fake_parse_intent
    )
    monkeypatch.setattr(
        NaturalLanguageRecommendationService,
        "explain_matches",
        fake_explain_matches,
    )

    response = client.post(
        "/api/recommend/natural-language",
        json={"prompt": "Find cash ETFs without crypto."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] > 0
    assert payload["narrative"] == "These instruments match the requested cash sleeve."
    assert all(
        instrument["sleeve"] == "cash" and instrument["crypto"] is False
        for instrument in payload["matched_instruments"]
    )


def test_natural_language_endpoint_validates_prompt() -> None:
    response = client.post(
        "/api/recommend/natural-language",
        json={"prompt": "  "},
    )

    assert response.status_code == 422
