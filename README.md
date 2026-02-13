# Client → Opportunity → Delivery System

**Operations Manager Performance Task** — Services & AI Platform | California Public Sector

A working prototype demonstrating the design of a scalable system for managing clients, opportunities, and delivery from lead to kickoff.

## Contents

- **Prototype** — Streamlit web app with all required features
- **Presentation** — HTML slide deck for GitHub Pages

## Quick Start

### Run the Prototype Locally

```bash
cd prototype
pip install -r requirements.txt
python -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Deploy

- **Prototype:** Deploy to [Streamlit Community Cloud](https://share.streamlit.io/) — connect your GitHub repo and point to `prototype/app.py`
- **Presentation (GitHub Pages):** Push to GitHub, go to Settings → Pages → Source: Deploy from branch → Branch: main, Folder: `/docs`

## Features

| Part | Feature |
|------|---------|
| 1 | Client Account Profile — sections, create/edit, view |
| 2 | Lead to Delivery Flow — stages, ownership, handoffs |
| 3 | Guardrails — 5 guardrails + decision helper |
| 4 | Example Walkthrough — demo client scenario |
| 5 | Feedback Loops — Delivery→Sales, Profile enrichment |
| 6 | Incentive Alignment — tension + mechanism |
| 7 | System Overview — end-to-end, design decisions |
| + | Dashboard — metrics, client list |

## Project Structure

```
Operations Management/
├── prototype/           # Streamlit app
│   ├── app.py
│   ├── data.py
│   ├── pages/
│   └── requirements.txt
├── presentation/        # HTML presentation
│   └── index.html
└── README.md
```
