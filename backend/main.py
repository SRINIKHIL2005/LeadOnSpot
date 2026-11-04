from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import unicodedata

from scorer import calculate_score
from explainer import MODEL_ID, ExplanationServiceError, get_llm_explanation

app = FastAPI(title="Lead Scoring Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class LeadInput(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    company_name: Optional[str] = Field(default=None, max_length=200)
    website: Optional[str] = Field(default=None, max_length=500)
    job_title: Optional[str] = Field(default=None, max_length=150)
    industry: Optional[str] = Field(default=None, max_length=150)
    company_location: Optional[str] = Field(default=None, max_length=200)
    company_size: Optional[str] = Field(default=None, max_length=100)
    lead_source: Optional[str] = Field(default=None, max_length=150)
    requirement: Optional[str] = Field(default=None, max_length=3000)
    email: Optional[str] = Field(default=None, max_length=254)
    phone: Optional[str] = Field(default=None, max_length=50)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()
        if not value:
            return value

        normalized = unicodedata.normalize("NFC", value)
        has_letter = any(unicodedata.category(char).startswith("L") for char in normalized)
        allowed = all(
            unicodedata.category(char).startswith(("L", "M"))
            or char.isspace()
            or char in {"'", "’", "-", "."}
            for char in normalized
        )
        if not has_letter or not allowed:
            raise ValueError(
                "Name must contain letters; numbers and symbols are not allowed."
            )
        return normalized


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/score")
def score_lead(lead: LeadInput):
    lead_dict = lead.model_dump()

    # Reject completely empty submissions
    filled = [v for v in lead_dict.values() if v and str(v).strip()]
    if len(filled) < 2:
        raise HTTPException(status_code=400, detail="Please provide at least 2 fields to score a lead.")

    score_result = calculate_score(lead_dict)
    try:
        explanation = get_llm_explanation(lead_dict, score_result)
    except ExplanationServiceError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return {
        "lead_name": lead.name or "Unknown Lead",
        "company": lead.company_name or "Unknown Company",
        "score": score_result["final_score"],
        "classification": score_result["classification"],
        "confidence": score_result["confidence"],
        "quality_assessment": _quality_assessment(score_result["final_score"]),
        "explanation": explanation,
        "explanation_provider": "Amazon Bedrock",
        "explanation_model": MODEL_ID,
        "positive_factors": score_result["positive_factors"],
        "negative_factors": score_result["negative_factors"],
        "next_action": score_result["next_action"],
        "score_breakdown": score_result["dimension_scores"],
    }


def _quality_assessment(score: float) -> str:
    if score >= 80:
        return "Excellent — High-value lead with strong buying signals"
    elif score >= 70:
        return "Good — Strong lead worth immediate attention"
    elif score >= 55:
        return "Average — Moderate potential, needs nurturing"
    elif score >= 40:
        return "Below Average — Low engagement signals"
    else:
        return "Poor — Insufficient data or low fit"
