# Flask Operations Dashboard — Command Center

Bootstrap 5 dashboard for the Client → Opportunity → Delivery system.

## Features

### Command Center Dashboard
- **Services vs AI Products** revenue balance with progress bars
- **Trust–Revenue Matrix** (4 quadrants): Prime targets (High Trust / Low AI), High-risk (Low Trust / High AI)
- **Guardrail Status Center** sidebar: flags opportunities violating guardrails
- **Future-Forward** Coming Soon: AI-Assisted CAP Enrichment, Synthetic Capacity Planner, Strategic Timing (Vedic-inspired)

### Interactive CAP (Client Account Profile)
- **Glassmorphism** card with 4 quadrants: Operational Context, Relationship Map, AI Readiness Score, Guardrail Flags
- **Toggle** between Services View (embedded team notes) and Product View (modular AI readiness)
- **Pulsing red border** when guardrails are violated

### Lead-to-Delivery Kanban
- Columns: Qualified Lead, Discovery, Proposal, Contract, Kickoff
- **Quality Gate**: Card cannot move Proposal → Contract unless AI Readiness Score ≥ 50
- **Role-Based Ownership**: Select your role (Sales/Ops/Delivery); drag blocked if not Primary Owner
- **SortableJS** for drag-and-drop

### Guardrails & Validation
- **`/validate_deal/<client_id>`**: Returns warning if Legacy Systems present but no Data Foundation Service
- **Toast notifications** when guardrails are violated

## Setup

```bash
cd flask_app
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000

## Routes

| Route | Description |
|-------|-------------|
| `/dashboard` | Command Center: Services/AI balance, Trust-Revenue matrix, Guardrail sidebar |
| `/kanban` | Lead-to-Delivery pipeline with drag-and-drop |
| `/clients` | Priority Score table |
| `/client/<id>` | Interactive CAP with Services/Product toggle |
| `/validate_deal/<id>` | Guardrail check (returns JSON) |
| `/analyze-account/<id>` | LLM analysis → save to CAP |
| `/api/opportunity/<id>/move` | Move opportunity (POST, enforces Quality Gate & Ownership) |
