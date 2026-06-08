# CertPilot X

CertPilot X is a synthetic-data-only, multi-agent certification intelligence demo built for the Microsoft Agents League reasoning challenge.

## What It Does

The app maps roles to certifications, generates adaptive study plans, adjusts for workload, predicts readiness, and surfaces team-level risk and coverage for managers.

## Key Views

- Employee Dashboard: personalized pathway, study plan, readiness score, and next actions.
- Manager Dashboard: team readiness, risk distribution, skill gaps, and certification coverage.
- Agent Trace Dashboard: reasoning trace, critic review, confidence scoring, and evaluation evidence.

## Architecture

See [architecture.md](architecture.md) for the system diagram and component breakdown.

## Synthetic Data Policy

All identifiers and datasets in this repo are fabricated. No real employee, customer, or secret data is used.

## Run Locally

1. Install dependencies: `pip install -r requirements.txt`
2. Launch the app: `streamlit run app.py`

## Repository Layout

- `app.py` - Streamlit UI
- `agents/` - curator, planner, engagement, predictor, critic
- `core/` - models, config, logging, tracing, validation, telemetry
- `orchestrator/` - workflow execution and manager insights
- `evaluation/` - synthetic evaluation runner
- `data/` - synthetic datasets and test cases
- `knowledge/` - grounding notes used by the demo

## Azure Readiness

The code includes scaffolded hooks for future Azure AI Foundry and MCP integration without changing the current demo flow.
