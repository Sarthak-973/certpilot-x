"""CertPilot X - enterprise certification intelligence dashboard."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.config import load_settings
from core.data_access import SyntheticDataRepository
from core.models import WorkflowRequest, WorkflowResult
from core.validators import ValidationError
from evaluation.runner import EvaluationRunner
from orchestrator.workflow import CertificationWorkflowOrchestrator


st.set_page_config(
    page_title="CertPilot X",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem;}
    .hero {
        padding: 1.5rem 1.6rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 52%, #06b6d4 100%);
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.18);
    }
    .hero h1 {margin: 0; font-size: 2.4rem; line-height: 1.05;}
    .hero p {margin: 0.55rem 0 0 0; opacity: 0.92; max-width: 60ch;}
    .surface {
        border: 1px solid #e2e8f0;
        background: #ffffff;
        border-radius: 18px;
        padding: 1rem 1rem 0.5rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def build_services() -> dict[str, Any]:
    settings = load_settings()
    repository = SyntheticDataRepository(settings)
    orchestrator = CertificationWorkflowOrchestrator(repository=repository, settings=settings)
    evaluation = EvaluationRunner(orchestrator=orchestrator, repository=repository, settings=settings)
    return {
        "settings": settings,
        "repository": repository,
        "orchestrator": orchestrator,
        "evaluation": evaluation,
    }


services = build_services()


def kpi(label: str, value: str, delta: str | None = None) -> None:
    st.metric(label, value, delta)


def render_gauge(title: str, value: int, threshold: int) -> None:
    chart = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0f766e"},
                "steps": [
                    {"range": [0, 60], "color": "#fee2e2"},
                    {"range": [60, 80], "color": "#fef3c7"},
                    {"range": [80, 100], "color": "#dcfce7"},
                ],
                "threshold": {"line": {"color": "#ef4444", "width": 4}, "thickness": 0.8, "value": threshold},
            },
        )
    )
    st.plotly_chart(chart, use_container_width=True)


def build_request_from_controls() -> WorkflowRequest:
    settings = services["settings"]
    role = st.sidebar.selectbox("Role", ["Data Engineer", "Data Analyst"], index=0)
    certification = st.sidebar.selectbox("Certification", ["DP-203", "PL-300"], index=0)
    weekly_hours = st.sidebar.slider("Weekly Study Hours", settings.min_weekly_hours, settings.max_weekly_hours, settings.default_weekly_hours)
    practice_score = st.sidebar.slider("Practice Score", 0, 100, settings.default_practice_score)
    meeting_hours = st.sidebar.slider("Meeting Hours", 0, 30, settings.default_meeting_hours)
    focus_hours = st.sidebar.slider("Focus Hours", 0, 30, settings.default_focus_hours)
    exam_date = st.sidebar.date_input("Exam Date", date.today() + timedelta(days=settings.default_exam_days))

    return WorkflowRequest(
        learner_id="L-UI-001",
        role=role,
        certification=certification,
        weekly_hours=weekly_hours,
        practice_score=practice_score,
        meeting_hours=meeting_hours,
        focus_hours=focus_hours,
        exam_date=exam_date.isoformat(),
    )


def employee_dashboard(result: WorkflowResult | None, request: WorkflowRequest) -> None:
    st.markdown(
        "<div class='hero'><h1>CertPilot X</h1><p>Enterprise certification intelligence for employees, managers, and auditors. The workflow maps role to certification, plans study time, adapts to workload, predicts success, and validates recommendations.</p></div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1.6])
    with left:
        st.markdown("<div class='surface'>", unsafe_allow_html=True)
        st.subheader("Learning Path Inputs")
        st.write(f"Access role: **Employee**")
        st.write(f"Current selection: **{request.role} / {request.certification}**")
        st.write(f"Exam date: **{request.exam_date}**")
        run_clicked = st.button("Run Reasoning Workflow", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if run_clicked:
        try:
            st.session_state.workflow_result = services["orchestrator"].execute(request)
        except ValidationError as exc:
            st.error(str(exc))
            return

    result = result or st.session_state.get("workflow_result")
    if result is None:
        st.info("Run the workflow to generate the employee learning path, planning output, readiness score, and critic review.")
        return

    with right:
        st.markdown("<div class='surface'>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi("Readiness", f"{result.prediction.readiness_score}")
        with c2:
            kpi("Pass Probability", f"{result.prediction.pass_probability}%")
        with c3:
            kpi("Risk Level", result.prediction.risk_level)
        with c4:
            kpi("Critic Confidence", f"{round(result.critic.confidence * 100)}%")

        render_gauge("Employee Readiness", result.prediction.readiness_score, services["settings"].readiness_threshold)
        st.markdown("</div>", unsafe_allow_html=True)

    path_col, plan_col = st.columns(2)
    with path_col:
        st.subheader("Learning Path")
        st.write(result.curator.explanation)
        st.write(
            {
                "role": result.curator.role,
                "certification": result.curator.certification,
                "skills": result.curator.skills,
                "recommended_hours": result.curator.recommended_hours,
            }
        )

        st.subheader("Recommended Next Actions")
        actions = [
            f"Study window: {result.engagement.best_study_window}",
            f"Recommended study increase: {result.prediction.recommended_study_increase} hours",
            f"Expected readiness improvement: {result.prediction.expected_readiness_improvement}",
        ]
        for action in actions:
            st.write(f"• {action}")

    with plan_col:
        st.subheader("Adaptive Study Plan")
        weeks_df = pd.DataFrame([week.to_dict() for week in result.study_plan.weeks])
        st.dataframe(weeks_df, use_container_width=True, hide_index=True)
        st.write(result.study_plan.plan_summary)
        st.write(f"**Allocated hours:** {result.study_plan.allocated_hours} / {result.study_plan.recommended_hours}")

    insight_col, validation_col = st.columns(2)
    with insight_col:
        st.subheader("Decision Explanations")
        st.write(result.prediction.explanation)
        st.write(result.engagement.explanation)
    with validation_col:
        st.subheader("Critic Review")
        st.write(f"**Verdict:** {result.critic.verdict}")
        st.write(f"**Confidence:** {round(result.critic.confidence * 100)}%")
        st.write(f"**Issues:** {', '.join(result.critic.issues) if result.critic.issues else 'None'}")
        st.write(f"**Warnings:** {', '.join(result.critic.warnings) if result.critic.warnings else 'None'}")
        if result.critic.self_reflection:
            st.caption("Self-reflection loop")
            for note in result.critic.self_reflection:
                st.write(f"• {note}")

    trace_df = pd.DataFrame([step.to_dict() for step in result.trace])
    st.subheader("Reasoning Snapshot")
    st.plotly_chart(
        px.bar(trace_df, x="agent", y="confidence", color="decision", text="decision", title="Agent Confidence by Step"),
        use_container_width=True,
    )


def manager_dashboard() -> None:
    st.markdown(
        "<div class='hero'><h1>Manager Dashboard</h1><p>Certification pipeline visibility, risk concentration, skill gaps, and team-level readiness analytics.</p></div>",
        unsafe_allow_html=True,
    )

    team_results, bundle = services["orchestrator"].analyze_team()
    team_rows = [
        {
            "learner_id": result.request.learner_id,
            "role": result.request.role,
            "certification": result.request.certification,
            "meeting_hours": result.request.meeting_hours,
            "focus_hours": result.request.focus_hours,
            "readiness_score": result.prediction.readiness_score,
            "pass_probability": result.prediction.pass_probability,
            "risk_level": result.prediction.risk_level,
            "critic_verdict": result.critic.verdict,
        }
        for result in team_results
    ]
    team_df = pd.DataFrame(team_rows)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Team Readiness", f"{bundle.team_readiness_pct}%")
    with c2:
        kpi("At-Risk Employees", str(len(bundle.at_risk_employees)))
    with c3:
        kpi("Coverage Tracks", str(len(bundle.certification_coverage)))
    with c4:
        kpi("Avg Confidence", f"{round(sum(r.critic.confidence for r in team_results) / max(1, len(team_results)) * 100)}%")

    left, right = st.columns(2)
    with left:
        st.subheader("Risk Distribution")
        risk_df = pd.DataFrame(list(bundle.risk_distribution.items()), columns=["risk", "count"])
        st.plotly_chart(px.pie(risk_df, names="risk", values="count", title="Team Risk Distribution"), use_container_width=True)

    with right:
        st.subheader("Risk Heatmap")
        st.plotly_chart(
            px.density_heatmap(
                team_df,
                x="meeting_hours",
                y="readiness_score",
                color_continuous_scale="Reds",
                nbinsx=6,
                nbinsy=6,
                title="Meeting Load vs Readiness",
            ),
            use_container_width=True,
        )

    coverage_col, skill_col = st.columns(2)
    with coverage_col:
        st.subheader("Certification Coverage")
        coverage_df = pd.DataFrame(list(bundle.certification_coverage.items()), columns=["certification", "count"])
        st.plotly_chart(px.bar(coverage_df, x="certification", y="count", text="count", title="Certification Coverage"), use_container_width=True)
    with skill_col:
        st.subheader("Skill Gap Analysis")
        gap_df = pd.DataFrame(list(bundle.skill_gap_analysis.items()), columns=["skill", "count"]) if bundle.skill_gap_analysis else pd.DataFrame(columns=["skill", "count"])
        if not gap_df.empty:
            st.plotly_chart(px.bar(gap_df, x="skill", y="count", text="count", title="Team Skill Gaps"), use_container_width=True)
        else:
            st.success("No material skill gaps detected in this synthetic cohort.")

    pipeline_df = pd.DataFrame(bundle.pipeline_summary)
    st.subheader("Certification Pipeline")
    st.plotly_chart(px.bar(pipeline_df, x="stage", y="count", text="count", title="Pipeline Progress"), use_container_width=True)

    st.subheader("Recommended Interventions")
    for intervention in bundle.recommended_interventions:
        st.write(f"• {intervention}")

    st.subheader("Team Readiness Table")
    st.dataframe(team_df, use_container_width=True, hide_index=True)


def trace_dashboard() -> None:
    st.markdown(
        "<div class='hero'><h1>Agent Trace Dashboard</h1><p>Reasoning flow, critic validation, confidence scoring, and synthetic evaluation evidence for hackathon judges and future Azure AI Foundry integration.</p></div>",
        unsafe_allow_html=True,
    )

    result: WorkflowResult | None = st.session_state.get("workflow_result")
    if result is None:
        st.info("Run the employee workflow first to generate a traceable reasoning path.")
    else:
        trace_df = pd.DataFrame([step.to_dict() for step in result.trace])
        st.subheader("Reasoning Flow")
        st.dataframe(trace_df[["timestamp", "agent", "action", "confidence", "decision"]], use_container_width=True, hide_index=True)
        st.subheader("Trace Confidence")
        st.plotly_chart(px.line(trace_df, x="agent", y="confidence", markers=True, title="Agent Confidence Across the Workflow"), use_container_width=True)
        st.subheader("Critic Validation")
        st.write(f"**Verdict:** {result.critic.verdict}")
        st.write(f"**Explanation:** {result.critic.explanation}")
        st.write(f"**Self reflection:** {', '.join(result.self_reflection) if result.self_reflection else 'None'}")

    st.subheader("Synthetic Evaluation Lab")
    if st.button("Run Evaluation Suite"):
        evaluation_report = services["evaluation"].run()
        st.session_state.evaluation_report = evaluation_report

    evaluation_report = st.session_state.get("evaluation_report")
    if evaluation_report is not None:
        st.write(evaluation_report.to_dict())


def footer() -> None:
    st.sidebar.markdown("### Access Mode")
    access_mode = st.sidebar.selectbox("Role-based access", ["Employee", "Manager", "Auditor"], index=0)
    st.sidebar.markdown("### Future Integration")
    st.sidebar.write("Foundry IQ for knowledge grounding. Work IQ for workload-aware scheduling. Fabric IQ for semantic readiness analytics.")
    st.sidebar.caption("MCP and Azure AI Foundry hooks are scaffolded in core/integration_hooks.py.")
    return access_mode


def main() -> None:
    settings = services["settings"]
    access_mode = footer()
    page = st.sidebar.radio("Dashboard", ["Employee Dashboard", "Manager Dashboard", "Agent Trace Dashboard"])
    request = build_request_from_controls()

    if page == "Employee Dashboard":
        employee_dashboard(st.session_state.get("workflow_result"), request)
    elif page == "Manager Dashboard":
        if access_mode == "Employee":
            st.warning("Switch the access mode to Manager or Auditor to view team-level insights.")
        manager_dashboard()
    else:
        if access_mode == "Employee":
            st.info("Trace visibility is typically reserved for managers, auditors, and platform owners.")
        trace_dashboard()

    st.sidebar.divider()
    st.sidebar.markdown("### Challenge Alignment")
    st.sidebar.write("• Reasoning agents with planner, engagement, predictor, critic loops")
    st.sidebar.write("• Synthetic data only")
    st.sidebar.write("• Microsoft IQ mapping and Azure Foundry hooks")


if __name__ == "__main__":
    main()
