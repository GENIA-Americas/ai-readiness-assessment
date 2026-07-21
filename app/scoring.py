from app.schemas import QuestionnaireResponses

# Each category is the average of its two questions (0-5), then weighted.
# Weights sum to 1.0.
CATEGORY_WEIGHTS = {
    "data_readiness": 0.25,
    "talent": 0.20,
    "governance": 0.20,
    "infrastructure": 0.20,
    "leadership": 0.15,
}

MAX_CATEGORY_SCORE = 5.0


def score_assessment(responses: QuestionnaireResponses) -> tuple[dict, float, str]:
    category_raw = {
        "data_readiness": (responses.data_centralized + responses.data_quality_process) / 2,
        "talent": (responses.ai_literate_staff + responses.dedicated_owner) / 2,
        "governance": (responses.has_ai_policy + responses.risk_review_process) / 2,
        "infrastructure": (responses.cloud_or_api_access + responses.integration_capacity) / 2,
        "leadership": (responses.leadership_buy_in + responses.budget_allocated) / 2,
    }

    category_scores = {
        cat: {
            "score": round(raw, 2),
            "max_score": MAX_CATEGORY_SCORE,
            "weight": CATEGORY_WEIGHTS[cat],
        }
        for cat, raw in category_raw.items()
    }

    # overall = weighted sum, normalized to a 0-100 scale
    weighted_sum = sum(
        category_raw[cat] * CATEGORY_WEIGHTS[cat] for cat in CATEGORY_WEIGHTS
    )
    overall_score = round((weighted_sum / MAX_CATEGORY_SCORE) * 100, 2)

    readiness_tier = tier_for_score(overall_score)

    return category_scores, overall_score, readiness_tier


def tier_for_score(overall_score: float) -> str:
    if overall_score >= 80:
        return "AI-Ready"
    if overall_score >= 60:
        return "Emerging"
    if overall_score >= 35:
        return "Foundational"
    return "Not Yet Ready"
