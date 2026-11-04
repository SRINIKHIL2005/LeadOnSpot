from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional

from scorer import calculate_score
from explainer import get_llm_explanation

app = FastAPI(title="Lead Scoring Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class LeadInput(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    website: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company_location: Optional[str] = None
    company_size: Optional[str] = None
    lead_source: Optional[str] = None
    requirement: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


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
    explanation = get_llm_explanation(lead_dict, score_result)

    return {
        "lead_name": lead.name or "Unknown Lead",
        "company": lead.company_name or "Unknown Company",
        "score": score_result["final_score"],
        "classification": score_result["classification"],
        "confidence": score_result["confidence"],
        "quality_assessment": _quality_assessment(score_result["final_score"]),
        "explanation": explanation,
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
