# CertPilot X

![Streamlit](https://img.shields.io/badge/Streamlit-1.37.1-FF4B4B?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge)
![Status](https://img.shields.io/badge/Hackathon-Submission%20Ready-0EA5E9?style=for-the-badge)

**Multi-Agent Enterprise Certification Intelligence Platform**

CertPilot X is a judge-ready Streamlit application that uses a coordinated set of reasoning agents to recommend certification paths, generate adaptive study plans, analyze workload impact, and surface team-level readiness insights from synthetic employee data.

## Problem Statement

Organizations struggle to help employees choose the right certification, maintain momentum, and balance study with work. Most learning tools are either too generic, too manual, or too disconnected from real workload conditions.

## Why Existing Solutions Fail

- They recommend courses without reasoning about role, skills, or certification target.
- They ignore workload, meeting load, and realistic study windows.
- They do not provide explainability for managers or auditors.
- They usually focus on one learner at a time and miss team-level risk patterns.
- They are rarely designed with traceability, evaluation, or synthetic demo safety in mind.

## Our Solution

CertPilot X combines a Streamlit experience with a multi-agent orchestration layer that turns one user request into a structured certification plan. The system maps role to certification, evaluates readiness, adapts around work constraints, and produces manager-facing insights backed by a reasoning trace.

## Key Features

- Employee dashboard for personalized certification planning.
- Manager dashboard for team readiness, skill gaps, and risk concentration.
- Agent trace dashboard for explainability and evaluation evidence.
- Synthetic data pipeline for safe demo environments.
- Orchestrated multi-agent workflow with planner, engagement, predictor, curator, and critic roles.
- Knowledge base support for certification guides and workload reports.
- Evaluation runner for hackathon credibility and repeatable scoring.

## Multi-Agent Architecture

CertPilot X uses a workflow orchestrator to coordinate specialized agents instead of one monolithic model call. Each agent owns a narrow responsibility and emits structured output for the next stage.

| Agent | Responsibility | Output |
| --- | --- | --- |
| Curator Agent | Maps role to certification and required skills | Certification profile and pathway explanation |
| Planner Agent | Builds a realistic weekly study plan | Study plan weeks, hours, and milestones |
| Engagement Agent | Adapts around workload and focus time | Best study window and workload band |
| Predictor Agent | Estimates readiness and pass probability | Risk level, readiness score, and recommended increase |
| Critic Agent | Validates realism and plan quality | Verdict, issues, warnings, and self-reflection |
| Manager Insights Engine | Aggregates team-wide readiness signals | Coverage, risk distribution, and interventions |

## System Workflow

1. A user selects a role, certification, workload, and exam timeline.
2. The orchestrator invokes the Curator Agent to resolve the certification path.
3. The Planner Agent creates a week-by-week learning plan.
4. The Engagement Agent recommends study windows around meetings and focus hours.
5. The Predictor Agent estimates readiness, pass probability, and risk.
6. The Critic Agent checks realism and can trigger a self-reflection adjustment.
7. The manager layer aggregates team analytics and highlights interventions.

## Technology Stack

| Layer | Technology |
| --- | --- |
| UI | Streamlit |
| DataFrames and analytics | pandas |
| Charts | Plotly |
| Workflow | Python orchestration layer |
| Models | Python dataclasses and typed contracts |
| Storage | Synthetic JSON datasets |
| Evaluation | Synthetic test case runner |

## Folder Structure

```text
app.py
agents/
core/
data/
evaluation/
knowledge/
orchestrator/
ui/
requirements.txt
```

## Installation Guide

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Confirm the synthetic data files are present in `data/`.

## Running Locally

```bash
streamlit run app.py
```

The app opens with employee, manager, and agent trace dashboards.

## Sample Use Cases

- An employee wants to know whether DP-203 or PL-300 is the better next certification.
- A manager wants to identify learners with high meeting load and low readiness.
- A team lead wants a realistic weekly plan that balances certification prep with focus time.
- A judge wants evidence of traceability, reasoning depth, and evaluation support.

## Business Impact

- Improves certification planning quality.
- Reduces manual coaching overhead.
- Surfaces team risk earlier.
- Helps align learning investment with workload reality.
- Makes certification programs easier to explain to leadership.

## Screenshots

- Employee Dashboard screenshot placeholder.
- Manager Dashboard screenshot placeholder.
- Agent Trace Dashboard screenshot placeholder.
- Evaluation Lab screenshot placeholder.

## Demo Video

- Demo video placeholder: add your recorded walkthrough URL here.

## Team

- Product and engineering demo by the CertPilot X hackathon team.
- Suggested structure: product lead, agent architect, UI engineer, data engineer, and demo presenter.

## License

This repository is intended for hackathon evaluation and internal demo use. Add your preferred license before publishing publicly.

## Architecture

See [architecture.md](architecture.md) for the detailed system architecture and Mermaid diagrams.
