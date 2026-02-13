"""
LLM integration for extracting insights from Delivery Team Notes.
Uses OpenAI API (placeholder when key not set - returns mock data).
"""

import json
import os
from typing import Dict, Any


def analyze_delivery_notes(notes: str, api_key: str = None) -> Dict[str, Any]:
    """
    Analyze Delivery Team Notes and extract:
    1) Potential AI Use Cases
    2) Technical Blockers
    3) Key Stakeholders

    Returns a JSON-serializable dict.
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    if api_key:
        return _call_openai(notes, api_key)
    return _mock_analysis(notes)


def _call_openai(notes: str, api_key: str) -> Dict[str, Any]:
    """Call OpenAI API for analysis. Uses openai package when available."""
    try:
        try:
            from openai import OpenAI
        except ImportError:
            return _mock_analysis(notes)
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are an analyst. Extract from the delivery notes and return ONLY valid JSON with these exact keys:
- potential_ai_use_cases: array of strings
- technical_blockers: array of strings  
- key_stakeholders: array of strings
No other text, only JSON."""
                },
                {"role": "user", "content": notes}
            ],
            temperature=0.3
        )
        text = response.choices[0].message.content.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        return {
            "potential_ai_use_cases": [f"API error: {str(e)}"],
            "technical_blockers": [],
            "key_stakeholders": []
        }


def _mock_analysis(notes: str) -> Dict[str, Any]:
    """Mock analysis when OpenAI API key is not configured."""
    notes_lower = (notes or "").lower()
    result = {
        "potential_ai_use_cases": [],
        "technical_blockers": [],
        "key_stakeholders": []
    }

    # Simple keyword-based extraction for demo
    if "automation" in notes_lower or "manual" in notes_lower:
        result["potential_ai_use_cases"].append("Process automation")
    if "report" in notes_lower or "analytics" in notes_lower:
        result["potential_ai_use_cases"].append("Analytics and reporting")
    if "compliance" in notes_lower:
        result["potential_ai_use_cases"].append("Compliance monitoring")
    if "legacy" in notes_lower or "erp" in notes_lower:
        result["technical_blockers"].append("Legacy system integration")
    if "api" in notes_lower or "integration" in notes_lower:
        result["technical_blockers"].append("API/integration constraints")
    if "stakeholder" in notes_lower or "manager" in notes_lower or "director" in notes_lower:
        result["key_stakeholders"].append("Senior leadership")
    if "it" in notes_lower or "technical" in notes_lower:
        result["key_stakeholders"].append("IT/Technical team")

    if not result["potential_ai_use_cases"]:
        result["potential_ai_use_cases"] = ["General process improvement (review notes for specifics)"]
    if not result["key_stakeholders"]:
        result["key_stakeholders"] = ["Account owner", "Delivery lead"]

    return result
