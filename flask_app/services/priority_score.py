"""Priority Score calculation: (Revenue * AI_Readiness) / Days_Since_Last_Update."""

from datetime import datetime, timezone


def calculate_priority_score(revenue: float, ai_readiness_score: int, last_delivery_update: datetime) -> float:
    """
    Priority = (Revenue * AI_Readiness) / Days_Since_Last_Update

    Returns 0 if days_since_update is 0 to avoid division by zero.
    """
    if revenue is None:
        revenue = 0.0
    if ai_readiness_score is None:
        ai_readiness_score = 0
    if last_delivery_update is None:
        last_delivery_update = datetime.utcnow()

    now = datetime.utcnow()
    if last_delivery_update.tzinfo:
        now = datetime.now(timezone.utc)
    delta = now - last_delivery_update
    days_since = max(delta.total_seconds() / 86400, 0.1)  # Min 0.1 days to avoid div by zero

    score = (revenue * ai_readiness_score) / days_since
    return round(score, 2)
