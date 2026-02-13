"""Guardrail validation logic for deals and opportunities."""

from datetime import datetime, timedelta
from typing import List, Tuple


def validate_deal(client) -> Tuple[bool, List[str]]:
    """
    Check guardrails for a client/deal.
    Returns (ok, list of warning messages).
    """
    warnings = []

    # 1. Services first: Legacy systems but no Data Foundation Service
    if client.legacy_systems and client.legacy_systems.strip():
        if not getattr(client, "data_foundation_service_active", False):
            warnings.append(
                "Services engagement required before AI Product adoption. "
                "Legacy systems detected but no Data Foundation Service active."
            )

    # 2. AI Product proposed without data audit
    ai_rev = getattr(client, "ai_product_revenue", 0) or 0
    if ai_rev > 0 and not getattr(client, "data_foundation_service_active", False):
        if client.legacy_systems and client.legacy_systems.strip():
            warnings.append(
                "AI Product proposed without data audit. Data Foundation Service recommended."
            )

    # 3. Product readiness: AI product without 6+ months engagement
    if ai_rev > 0:
        eng_start = getattr(client, "engagement_start_date", None) or getattr(client, "created_at", None)
        if eng_start:
            months = (datetime.utcnow() - eng_start).days / 30
            if months < 6:
                warnings.append(
                    "Product readiness: Client has < 6 months engagement. "
                    "Services engagement should precede AI product pilots."
                )

    # 4. Use case not documented before product proposal
    if ai_rev > 0 and not getattr(client, "use_case_documented", False):
        use_cases = getattr(client, "ai_use_cases", "[]") or "[]"
        if use_cases == "[]" or not use_cases.strip():
            warnings.append(
                "Use case must be documented before proposing AI product."
            )

    # 5. Delivery capacity not confirmed
    if ai_rev > 0 and not getattr(client, "delivery_capacity_confirmed", False):
        warnings.append(
            "Delivery capacity must be confirmed before committing to AI product."
        )

    # 6. Pilot before scale: AI product at scale without prior pilot
    if ai_rev > 50000 and not getattr(client, "prior_pilot_success", False):
        if not getattr(client, "data_foundation_service_active", False):
            warnings.append(
                "Pilot before scale: AI products should start as 3–6 month pilots "
                "unless client has prior successful pilot with us."
            )

    # 7. Budget not confirmed before proposal
    if not getattr(client, "budget_confirmed", False) and (client.revenue or 0) > 0:
        # Only flag if we have revenue but no explicit budget confirmation
        pass  # Optional - skip to avoid noise

    # 8. Handoff checklist incomplete (Sales → Ops)
    try:
        opps = list(client.opportunities) if hasattr(client, "opportunities") else []
        in_contract_or_kickoff = any(getattr(o, "stage", "") in ("contract", "kickoff") for o in opps)
        if in_contract_or_kickoff and not getattr(client, "handoff_checklist_complete", False):
            warnings.append(
                "Handoff checklist must be complete before contract signing."
            )
    except Exception:
        pass

    # 9. Trust preservation: Low trust + high AI = high risk
    trust = getattr(client, "trust_level", 50) or 50
    if trust < 50 and ai_rev > 0:
        warnings.append(
            "Trust preservation: Low trust account with AI product. "
            "Consider additional services support before scaling product."
        )

    # 10. New relationship proposing product
    eng_start = getattr(client, "engagement_start_date", None) or getattr(client, "created_at", None)
    if eng_start and ai_rev > 0:
        days = (datetime.utcnow() - eng_start).days
        if days < 90:
            warnings.append(
                "Services first: New relationship (< 90 days). "
                "Establish services engagement before AI product."
            )

    return (len(warnings) == 0, list(dict.fromkeys(warnings)))  # Dedupe


def get_guardrail_violations_for_clients(clients) -> List[dict]:
    """Return list of clients with guardrail violations for sidebar."""
    result = []
    for c in clients:
        ok, warnings = validate_deal(c)
        if not ok and warnings:
            result.append({"client": c, "warnings": warnings})
    return result


# Human-readable guardrail definitions for display
GUARDRAIL_DEFINITIONS = [
    {"id": 1, "title": "Services First", "rule": "Legacy systems require Data Foundation Service before AI Product."},
    {"id": 2, "title": "Data Audit", "rule": "AI Product proposed without data audit — recommend Data Foundation."},
    {"id": 3, "title": "6+ Months Engagement", "rule": "Product requires 6+ months prior engagement."},
    {"id": 4, "title": "Use Case Documented", "rule": "Use case must be documented before product proposal."},
    {"id": 5, "title": "Delivery Capacity", "rule": "Delivery capacity must be confirmed before committing."},
    {"id": 6, "title": "Pilot Before Scale", "rule": "AI products start as pilots unless prior success."},
    {"id": 7, "title": "Handoff Checklist", "rule": "Complete handoff checklist before contract."},
    {"id": 8, "title": "Trust Preservation", "rule": "Low trust + AI product = add services support."},
    {"id": 9, "title": "New Relationship", "rule": "Establish services (< 90 days) before product."},
]
