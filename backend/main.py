from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator
from typing import Optional
import unicodedata
import re

if __package__:
    from .explainer import MODEL_ID, ExplanationServiceError, get_llm_explanation
    from .scorer import calculate_score
else:
    from explainer import MODEL_ID, ExplanationServiceError, get_llm_explanation
    from scorer import calculate_score

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
    email: Optional[EmailStr] = Field(default=None, max_length=254)
    phone: Optional[str] = Field(default=None, max_length=50)

    @field_validator("*", mode="before")
    @classmethod
    def reject_zero_placeholders(cls, value: object, info: ValidationInfo) -> object:
        if isinstance(value, str) and re.fullmatch(r"\s*[+-]?0+(?:[.,]0+)?\s*", value):
            raise ValueError(
                f"{info.field_name.replace('_', ' ').capitalize()} cannot be zero; "
                "enter real information or leave it blank."
            )
        return value

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

    @field_validator(
        "company_name",
        "job_title",
        "industry",
        "company_location",
        "lead_source",
        "requirement",
    )
    @classmethod
    def validate_text_fields(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:
        if value is None or not value.strip():
            return value
        if not any(unicodedata.category(char).startswith("L") for char in value):
            raise ValueError(
                f"{info.field_name.replace('_', ' ').capitalize()} must contain letters."
            )
        return value.strip()

    @field_validator("website")
    @classmethod
    def validate_website(cls, value: Optional[str]) -> Optional[str]:
        if value is None or not value.strip():
            return value
        website = value.strip()
        domain = re.sub(r"^https?://", "", website, flags=re.IGNORECASE).split("/", 1)[0]
        domain = domain.split(":", 1)[0]
        if (
            not domain
            or "." not in domain
            or any(char.isspace() for char in website)
            or not re.fullmatch(r"[A-Za-z0-9.-]+", domain)
        ):
            raise ValueError("Enter a valid website, such as www.example.com.")
        return website

    @field_validator("company_size")
    @classmethod
    def validate_company_size(cls, value: Optional[str]) -> Optional[str]:
        if value is None or not value.strip():
            return value
        size = value.strip()
        if not re.fullmatch(
            r"\d[\d,]*(?:\s*(?:-|–|—|to)\s*\d[\d,]*)?\s*\+?"
            r"(?:\s+(?:employees?|people|staff))?",
            size,
            flags=re.IGNORECASE,
        ):
            raise ValueError(
                "Enter a company size as a count or range, such as 50-100 employees."
            )
        numbers = re.findall(r"\d+", size.replace(",", ""))
        if not numbers or not any(int(number) > 0 for number in numbers):
            raise ValueError(
                "Company size must include a positive employee count, such as 50-100."
            )
        return value.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None or not value.strip():
            return value
        phone = value.strip()
        digits = re.sub(r"\D", "", phone)
        if not re.fullmatch(r"[+0-9(). /-]+", phone) or not 7 <= len(digits) <= 15:
            raise ValueError("Enter a valid phone number containing 7 to 15 digits.")
        return phone


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
        "explanation_provider": "Ollama (local)",
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
