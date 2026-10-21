from fastapi import APIRouter, HTTPException

from app.engine.universe import universe_service
from app.models.natural_language import (
    NaturalLanguageRecommendationResponse,
    NaturalLanguageRequest,
)
from app.services.natural_language_recommendation import (
    NaturalLanguageServiceError,
    natural_language_recommendation_service,
)

router = APIRouter()


@router.post(
    "/recommend/natural-language",
    response_model=NaturalLanguageRecommendationResponse,
    tags=["Recommendations"],
)
async def recommend_from_natural_language(
    request: NaturalLanguageRequest,
) -> NaturalLanguageRecommendationResponse:
    if not universe_service.instruments:
        raise HTTPException(
            status_code=503,
            detail="The instrument universe is unavailable.",
        )

    service = natural_language_recommendation_service
    try:
        filters = await service.parse_intent(request.prompt)
        matches = service.filter_instruments(filters)
        narrative = await service.explain_matches(request.prompt, filters, matches)
    except NaturalLanguageServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    return NaturalLanguageRecommendationResponse(
        filters=filters,
        count=len(matches),
        matched_instruments=matches,
        narrative=narrative,
    )
