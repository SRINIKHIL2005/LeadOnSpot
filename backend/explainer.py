"""
LLM Explainer — uses AWS Bedrock (Claude) to generate a human-readable
scoring explanation. The score itself comes from scorer.py, NOT from the LLM.
"""

import json
import boto3
from botocore.exceptions import ClientError

# Claude model on Bedrock — change to claude-3-sonnet if you want richer output
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"


def build_prompt(lead: dict, score_result: dict) -> str:
    return f"""You are a sales analyst. A lead scoring algorithm has already calculated a score for this lead.
Your job is to write a clear, concise 3–4 sentence explanation of WHY this lead received this score.
Base your explanation ONLY on the data provided. Do not invent information.

Lead Data:
- Name: {lead.get('name', 'N/A')}
- Company: {lead.get('company_name', 'N/A')}
- Job Title: {lead.get('job_title', 'N/A')}
- Industry: {lead.get('industry', 'N/A')}
- Company Size: {lead.get('company_size', 'N/A')}
- Lead Source: {lead.get('lead_source', 'N/A')}
- Requirement: {lead.get('requirement', 'N/A')}
- Location: {lead.get('company_location', 'N/A')}

Algorithm Score: {score_result['final_score']}/100
Classification: {score_result['classification']}
Positive Factors: {', '.join(score_result['positive_factors']) if score_result['positive_factors'] else 'None'}
Negative Factors: {', '.join(score_result['negative_factors']) if score_result['negative_factors'] else 'None'}

Write a 3–4 sentence explanation. Be specific, factual, and professional. No bullet points."""


def get_llm_explanation(lead: dict, score_result: dict) -> str:
    """Call AWS Bedrock Claude to generate explanation. Returns plain text."""
    try:
        client = boto3.client("bedrock-runtime", region_name="us-east-1")
        prompt = build_prompt(lead, score_result)

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        result = json.loads(response["body"].read())
        return result["content"][0]["text"].strip()

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ("AccessDeniedException", "UnrecognizedException"):
            return _fallback_explanation(lead, score_result)
        raise
    except Exception:
        return _fallback_explanation(lead, score_result)


def _fallback_explanation(lead: dict, score_result: dict) -> str:
    """Rule-based explanation when Bedrock is unavailable."""
    name = lead.get("name", "This lead")
    score = score_result["final_score"]
    classification = score_result["classification"]
    positives = score_result["positive_factors"]
    negatives = score_result["negative_factors"]

    explanation = f"{name} received a score of {score}/100, classifying them as a {classification} lead. "

    if positives:
        explanation += f"Key strengths include: {'; '.join(positives[:2])}. "
    if negatives:
        explanation += f"Areas of concern: {'; '.join(negatives[:2])}. "

    explanation += f"The recommended next action is: {score_result['next_action']}"
    return explanation
