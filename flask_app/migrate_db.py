"""Add new columns to existing database. Run once if upgrading from older schema."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "instance" / "clients.db"
# New tables (users, leads, client_permissions) are created by db.create_all()
NEW_COLUMNS = [
    ("clients", "assigned_to_id", "INTEGER"),
    ("clients", "approver_id", "INTEGER"),
    ("clients", "ai_feature_request", "TEXT DEFAULT ''"),
    ("clients", "services_revenue", "REAL DEFAULT 0"),
    ("clients", "ai_product_revenue", "REAL DEFAULT 0"),
    ("clients", "trust_level", "INTEGER DEFAULT 50"),
    ("clients", "data_foundation_service_active", "BOOLEAN DEFAULT 0"),
    ("clients", "guardrail_flags", "TEXT DEFAULT '[]'"),
    ("clients", "problem_priority", "TEXT DEFAULT ''"),
    ("clients", "engagement_start_date", "DATETIME DEFAULT NULL"),
    ("clients", "use_case_documented", "BOOLEAN DEFAULT 0"),
    ("clients", "delivery_capacity_confirmed", "BOOLEAN DEFAULT 0"),
    ("clients", "prior_pilot_success", "BOOLEAN DEFAULT 0"),
    ("clients", "budget_confirmed", "BOOLEAN DEFAULT 0"),
    ("clients", "handoff_checklist_complete", "BOOLEAN DEFAULT 0"),
]


def migrate():
    if not DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for table, col, spec in NEW_COLUMNS:
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {spec}")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                raise
    conn.commit()
    conn.close()


if __name__ == "__main__":
    migrate()
    print("Migration complete.")
