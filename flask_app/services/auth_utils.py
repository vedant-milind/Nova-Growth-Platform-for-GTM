"""Auth and permission utilities for role-based access control."""

from flask_login import current_user
from models import ROLE_CEO, ROLE_STRATEGY_LEAD, ClientPermission


def can_view_confidential(client):
    """True if current user can see confidential client data (revenue, CAP details, etc.)."""
    if not current_user or not current_user.is_authenticated:
        return False
    if current_user.has_full_access():
        return True
    return ClientPermission.query.filter_by(
        user_id=current_user.id, client_id=client.id
    ).first() is not None


def can_grant_permissions():
    """True if user can grant confidential access to employees (CEO, Strategy Lead)."""
    if not current_user or not current_user.is_authenticated:
        return False
    return current_user.role in (ROLE_CEO, ROLE_STRATEGY_LEAD)


def filter_clients_for_user(clients):
    """Return clients the user can see. Employees see all clients but confidential data is masked per-client."""
    return clients  # All clients visible; confidential fields masked in templates
