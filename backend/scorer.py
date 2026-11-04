"""
Lead Scoring Engine — Rule-based weighted algorithm.
All weights and rules are defined here. Edit freely.
"""

from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# SCORING RULES — edit these to tune the system
# ─────────────────────────────────────────────

# Job titles mapped to decision-maker score (0–100)
JOB_TITLE_SCORES = {
    # C-Suite / Founders
    "founder": 100, "co-founder": 100, "ceo": 100, "cto": 100, "coo": 100, "cfo": 100,
    "chief executive": 100, "chief technology": 100, "chief operating": 100,
    # VP / Directors
    "vp": 85, "vice president": 85, "director": 80, "head of": 80,
    # Managers
    "manager": 60, "lead": 55, "senior manager": 65,
    # Individual contributors
    "engineer": 30, "developer": 30, "analyst": 35, "consultant": 45,
    "executive": 50, "associate": 25, "intern": 5,
}

# Company size ranges mapped to score (0–100)
# Key = (min_employees, max_employees), Value = score
COMPANY_SIZE_SCORES = [
    (1, 10, 30),        # Micro — low budget
    (11, 50, 55),       # Small
    (51, 200, 80),      # Mid-market — sweet spot
    (201, 1000, 90),    # Large
    (1001, 999999, 70), # Enterprise — long sales cycle
]

# Industries and their fit score (0–100)
INDUSTRY_SCORES = {
    "it services": 100, "software": 100, "saas": 100, "technology": 95,
    "fintech": 90, "finance": 85, "banking": 80, "insurance": 75,
    "healthcare": 80, "edtech": 85, "education": 75,
    "ecommerce": 85, "retail": 70, "manufacturing": 65,
    "real estate": 60, "logistics": 65, "consulting": 75,
    "media": 60, "marketing": 70, "hr": 65,
}

# Lead source quality scores (0–100)
LEAD_SOURCE_SCORES = {
    "website": 90, "referral": 100, "linkedin": 85, "cold call": 50,
    "email campaign": 60, "social media": 65, "trade show": 75,
    "webinar": 80, "partner": 90, "inbound": 90, "outbound": 45,
    "advertisement": 55, "google": 70, "organic": 85,
}

# Requirement keywords that indicate high intent (each adds points)
HIGH_INTENT_KEYWORDS = [
    "crm", "erp", "automation", "integration", "software", "platform",
    "solution", "system", "tool", "implement", "deploy", "migrate",
    "upgrade", "replace", "looking for", "need", "require",
]

# Weights for each scoring dimension (must sum to 1.0)
WEIGHTS = {
    "job_title": 0.25,
    "company_size": 0.20,
    "industry": 0.15,
    "lead_source": 0.15,
    "requirement": 0.15,
    "contact_completeness": 0.10,
}

# Classification thresholds
HOT_THRESHOLD = 70
WARM_THRESHOLD = 40


# ─────────────────────────────────────────────
# SCORING LOGIC — modify with care
# ─────────────────────────────────────────────

@dataclass
class ScoreBreakdown:
    job_title_score: float = 0
    company_size_score: float = 0
    industry_score: float = 0
    lead_source_score: float = 0
    requirement_score: float = 0
    contact_completeness_score: float = 0
    positive_factors: list = field(default_factory=list)
    negative_factors: list = field(default_factory=list)


def score_job_title(title: Optional[str]) -> tuple[float, str]:
    if not title:
        return 0, "Job title missing"
    title_lower = title.lower().strip()
    for keyword, score in JOB_TITLE_SCORES.items():
        if keyword in title_lower:
            return score, f"Job title '{title}' indicates decision-maker level"
    return 40, f"Job title '{title}' — unknown level, assigned neutral score"


def score_company_size(size_str: Optional[str]) -> tuple[float, str]:
    if not size_str:
        return 0, "Company size missing"
    # Extract numbers from strings like "50-100", "50–100", "500+", "1000"
    import re
    numbers = re.findall(r'\d+', size_str.replace(',', ''))
    if not numbers:
        return 0, "Company size format unrecognized"
    # Use midpoint if range given, else the single number
    nums = [int(n) for n in numbers]
    midpoint = sum(nums) / len(nums)
    for min_e, max_e, score in COMPANY_SIZE_SCORES:
        if min_e <= midpoint <= max_e:
            return score, f"Company size '{size_str}' is in the {min_e}–{max_e} range"
    return 50, f"Company size '{size_str}' — assigned default score"


def score_industry(industry: Optional[str]) -> tuple[float, str]:
    if not industry:
        return 0, "Industry missing"
    industry_lower = industry.lower().strip()
    for key, score in INDUSTRY_SCORES.items():
        if key in industry_lower or industry_lower in key:
            return score, f"Industry '{industry}' is a strong fit"
    return 40, f"Industry '{industry}' — not in high-fit list, assigned neutral score"


def score_lead_source(source: Optional[str]) -> tuple[float, str]:
    if not source:
        return 0, "Lead source missing"
    source_lower = source.lower().strip()
    for key, score in LEAD_SOURCE_SCORES.items():
        if key in source_lower or source_lower in key:
            return score, f"Lead source '{source}' has quality score {score}"
    return 50, f"Lead source '{source}' — unknown, assigned neutral score"


def score_requirement(requirement: Optional[str]) -> tuple[float, str]:
    if not requirement:
        return 0, "Requirement missing"
    req_lower = requirement.lower()
    matched = [kw for kw in HIGH_INTENT_KEYWORDS if kw in req_lower]
    # Score based on length and keyword matches
    length_score = min(len(requirement.split()) * 5, 50)  # up to 50 for detail
    keyword_score = min(len(matched) * 15, 50)            # up to 50 for keywords
    total = min(length_score + keyword_score, 100)
    return total, f"Requirement mentions: {', '.join(matched) if matched else 'no specific keywords'}"


def score_contact_completeness(lead: dict) -> tuple[float, str]:
    fields = ["name", "email", "phone", "company_name", "website"]
    present = [f for f in fields if lead.get(f) and str(lead[f]).strip()]
    score = (len(present) / len(fields)) * 100
    missing = [f for f in fields if f not in present]
    msg = f"{len(present)}/{len(fields)} contact fields present"
    if missing:
        msg += f" (missing: {', '.join(missing)})"
    return score, msg


def calculate_score(lead: dict) -> dict:
    bd = ScoreBreakdown()

    jt_score, jt_msg = score_job_title(lead.get("job_title"))
    cs_score, cs_msg = score_company_size(lead.get("company_size"))
    ind_score, ind_msg = score_industry(lead.get("industry"))
    ls_score, ls_msg = score_lead_source(lead.get("lead_source"))
    req_score, req_msg = score_requirement(lead.get("requirement"))
    cc_score, cc_msg = score_contact_completeness(lead)

    bd.job_title_score = jt_score
    bd.company_size_score = cs_score
    bd.industry_score = ind_score
    bd.lead_source_score = ls_score
    bd.requirement_score = req_score
    bd.contact_completeness_score = cc_score

    # Weighted final score
    final_score = (
        jt_score * WEIGHTS["job_title"] +
        cs_score * WEIGHTS["company_size"] +
        ind_score * WEIGHTS["industry"] +
        ls_score * WEIGHTS["lead_source"] +
        req_score * WEIGHTS["requirement"] +
        cc_score * WEIGHTS["contact_completeness"]
    )
    final_score = round(final_score, 1)

    # Classify
    if final_score >= HOT_THRESHOLD:
        classification = "Hot"
    elif final_score >= WARM_THRESHOLD:
        classification = "Warm"
    else:
        classification = "Cold"

    # Positive / Negative factors
    dimension_scores = {
        "Job Title": (jt_score, jt_msg),
        "Company Size": (cs_score, cs_msg),
        "Industry Fit": (ind_score, ind_msg),
        "Lead Source": (ls_score, ls_msg),
        "Requirement Clarity": (req_score, req_msg),
        "Contact Completeness": (cc_score, cc_msg),
    }
    positive_factors = [msg for dim, (sc, msg) in dimension_scores.items() if sc >= 60]
    negative_factors = [msg for dim, (sc, msg) in dimension_scores.items() if sc < 40]

    # Confidence: based on how many fields are filled
    filled_fields = sum(1 for k in ["name", "company_name", "job_title", "industry",
                                     "company_size", "lead_source", "requirement",
                                     "email", "phone"] if lead.get(k) and str(lead[k]).strip())
    confidence = round((filled_fields / 9) * 100)

    # Recommended action
    if classification == "Hot":
        next_action = "Assign to senior sales rep immediately. Schedule a demo call within 24 hours."
    elif classification == "Warm":
        next_action = "Add to nurture sequence. Follow up within 3–5 business days with relevant case studies."
    else:
        next_action = "Add to long-term nurture list. Send introductory content and re-evaluate in 30 days."

    return {
        "final_score": final_score,
        "classification": classification,
        "confidence": confidence,
        "next_action": next_action,
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "dimension_scores": {
            "job_title": {"score": jt_score, "detail": jt_msg, "weight": "25%"},
            "company_size": {"score": cs_score, "detail": cs_msg, "weight": "20%"},
            "industry": {"score": ind_score, "detail": ind_msg, "weight": "15%"},
            "lead_source": {"score": ls_score, "detail": ls_msg, "weight": "15%"},
            "requirement": {"score": req_score, "detail": req_msg, "weight": "15%"},
            "contact_completeness": {"score": cc_score, "detail": cc_msg, "weight": "10%"},
        },
    }
