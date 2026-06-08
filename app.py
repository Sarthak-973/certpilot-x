"""
CertPilot Streamlit Application
Multi-page app with Employee View and Manager View
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

# Import agents
from agents.curator_agent import CuratorAgent
from agents.planner_agent import PlannerAgent
from agents.engagement_agent import EngagementAgent
from agents.assessment_agent import AssessmentAgent
from agents.predictor_agent import PredictorAgent
from agents.manager_agent import ManagerAgent
from agents.critic_agent import CriticAgent

# Initialize agents
@st.cache_resource
def initialize_agents():
    return {
        "curator": CuratorAgent(),
        "planner": PlannerAgent(),
        "engagement": EngagementAgent(),
        "assessment": AssessmentAgent(),
        "predictor": PredictorAgent(),
        "manager": ManagerAgent(),
        "critic": CriticAgent()
    }

agents = initialize_agents()

# Page configuration
st.set_page_config(
    page_title="CertPilot - Certification Success Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success {
        color: #09ab3b;
        font-weight: bold;
    }
    .warning {
        color: #ff9500;
        font-weight: bold;
    }
    .danger {
        color: #ff2b2b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def employee_view():
    """Employee View - Individual certification path"""
    st.title("👤 Employee View - Certification Roadmap")
    st.markdown("Get your personalized certification success plan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Your Information")
        learner_id = st.text_input("Learner ID", "L1001")
        role = st.selectbox("Your Role", ["Data Engineer", "Cloud Architect", "DevOps Engineer", "AI/ML Specialist"])
        
    with col2:
        st.subheader("⏱️ Availability")
        hours_per_week = st.slider("Study hours per week", 1, 20, 5)
        meeting_hours = st.slider("Meeting hours per week", 0, 40, 20)
        focus_hours = st.slider("Focus hours per week", 0, 40, 12)
    
    exam_date = st.date_input("Target Exam Date", datetime.now() + timedelta(days=60))
    
    if st.button("🚀 Generate My Certification Plan", key="employee_generate"):
        st.session_state.employee_generated = True
    
    if st.session_state.get("employee_generated", False):
        st.divider()
        
        # Step 1: Curator - Learning Path
        with st.spinner("🎯 Building your learning path..."):
            curator_output = agents["curator"].curate_learning_path(role)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📚 Learning Path")
                st.metric("Certification", curator_output.get("certification", "N/A"))
                st.info("**Required Skills:**\n" + "\n".join([f"✓ {skill}" for skill in curator_output.get("skills", [])]))
            
            with col2:
                st.subheader("📦 Resources")
                resources = curator_output.get("resources", [])
                for i, resource in enumerate(resources, 1):
                    st.write(f"{i}. {resource}")
        
        # Step 2: Planner - Study Schedule
        with st.spinner("📅 Creating your study schedule..."):
            planner_output = agents["planner"].create_study_plan(
                hours_per_week=hours_per_week,
                exam_date=exam_date.strftime("%Y-%m-%d")
            )
            
            st.subheader("📅 Your Study Schedule")
            
            schedule_data = []
            for week in planner_output["weekly_schedule"][:4]:  # Show first 4 weeks
                schedule_data.append({
                    "Week": week["week"],
                    "Topic": week["topic"],
                    "Hours": week["hours"],
                    "Milestones": ", ".join(week["milestones"][:2])
                })
            
            df_schedule = pd.DataFrame(schedule_data)
            st.dataframe(df_schedule, use_container_width=True)
        
        # Step 3: Engagement - Work-Life Balance
        with st.spinner("⚖️ Analyzing your work-life balance (Work IQ)..."):
            engagement_output = agents["engagement"].analyze_workload(meeting_hours, focus_hours)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
                st.metric("Risk Level", f"{risk_color.get(engagement_output['risk_level'], '⚪')} {engagement_output['risk_level']}")
            
            with col2:
                study_window = agents["engagement"].find_study_window(meeting_hours)
                st.metric("Best Study Window", study_window)
            
            with col3:
                st.metric("Weekly Work Hours", f"{meeting_hours + focus_hours}h")
            
            st.warning(f"💡 {engagement_output['recommendation']}")
        
        # Step 4: Assessment - Current Knowledge
        with st.spinner("📝 Generating practice questions..."):
            practice_questions = agents["assessment"].generate_practice_questions(count=3)
            
            st.subheader("📝 Practice Assessment")
            
            # Mock assessment - in real app would be interactive
            mock_responses = [
                {"correct": True, "topic": "Azure Data Factory"},
                {"correct": False, "topic": "Synapse Analytics"},
                {"correct": True, "topic": "Data Storage"}
            ]
            
            assessment_result = agents["assessment"].assess_knowledge(mock_responses)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Practice Score", f"{assessment_result['score']}%")
            with col2:
                st.metric("Correct Answers", f"{assessment_result['correct_answers']}/{assessment_result['total_questions']}")
            with col3:
                st.metric("Readiness", assessment_result['readiness_score'])
        
        # Step 5: Predictor - Pass Probability (DIFFERENTIATOR)
        with st.spinner("🔮 Calculating your pass probability (CertPilot AI)..."):
            predictor_output = agents["predictor"].predict_pass_probability(
                practice_score=assessment_result['score'],
                study_hours=hours_per_week * 4,
                meeting_hours=meeting_hours
            )
            
            st.subheader("🔮 Success Prediction (CertPilot Differentiator)")
            
            # Create gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=predictor_output['pass_probability'],
                title={'text': "Pass Probability (%)"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "#ff2b2b"},
                        {'range': [50, 75], 'color': "#ff9500"},
                        {'range': [75, 100], 'color': "#09ab3b"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': predictor_output['pass_threshold']
                    }
                }
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                risk_emoji = {"LOW": "✅", "MEDIUM": "⚠️", "HIGH": "❌"}
                st.metric("Risk Assessment", f"{risk_emoji.get(predictor_output['risk_level'], '❓')} {predictor_output['risk_level']}")
            
            with col2:
                st.metric("Predicted Score", f"{predictor_output['predicted_score']:.1f}%")
            
            st.info(f"💬 {predictor_output['recommendation']}")
        
        # Step 6: Critic - Validation
        with st.spinner("🔍 Validating your plan..."):
            critic_output = agents["critic"].validate_study_plan(planner_output)
            readiness_check = agents["critic"].verify_readiness_criteria({
                "practice_score": assessment_result['score'],
                "hours_studied": hours_per_week * 4,
                "weak_areas": assessment_result['weak_areas']
            })
            
            st.subheader("✅ Plan Validation")
            
            if critic_output['is_valid']:
                st.success("✓ Your study plan is realistic and achievable!")
            else:
                st.error("✗ Your plan needs adjustment")
                for error in critic_output['errors']:
                    st.error(f"  • {error}")
            
            for warning in critic_output['warnings']:
                st.warning(f"  ⚠ {warning}")
        
        # Final Recommendation
        st.divider()
        st.subheader("🎯 Your Personalized Roadmap")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Key Metrics:**")
            st.write(f"• Certification: {curator_output.get('certification')}")
            st.write(f"• Study Duration: {planner_output['total_weeks']} weeks")
            st.write(f"• Success Rate: {predictor_output['pass_probability']}%")
            st.write(f"• Risk Level: {predictor_output['risk_level']}")
        
        with col2:
            st.write("**Next Steps:**")
            st.write(f"1. {engagement_output['recommendation']}")
            st.write(f"2. Best study window: {study_window}")
            if assessment_result['weak_areas']:
                st.write(f"3. Focus on: {', '.join(assessment_result['weak_areas'])}")
            st.write("4. Start with Week 1 topics immediately")


def manager_view():
    """Manager View - Team-level insights"""
    st.title("👔 Manager View - Team Certification Dashboard")
    st.markdown("Get insights into your team's certification readiness")
    
    # Load sample data
    sample_learners = [
        {"learner_id": "L1001", "role": "Data Engineer", "practice_score": 72, "hours_studied": 18, "meeting_hours": 20, "risk_level": "MEDIUM"},
        {"learner_id": "L1002", "role": "Data Engineer", "practice_score": 85, "hours_studied": 25, "meeting_hours": 15, "risk_level": "LOW"},
        {"learner_id": "L1003", "role": "Cloud Architect", "practice_score": 65, "hours_studied": 12, "meeting_hours": 35, "risk_level": "HIGH"},
        {"learner_id": "L1004", "role": "DevOps Engineer", "practice_score": 78, "hours_studied": 22, "meeting_hours": 18, "risk_level": "MEDIUM"},
        {"learner_id": "L1005", "role": "AI/ML Specialist", "practice_score": 92, "hours_studied": 28, "meeting_hours": 10, "risk_level": "LOW"},
    ]
    
    # Add learner data to manager agent
    manager = agents["manager"]
    for learner in sample_learners:
        manager.add_learner_data(learner)
    
    # Team Readiness Report
    st.subheader("📊 Team Readiness Report")
    
    readiness_report = manager.generate_team_readiness_report()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Learners", readiness_report['total_learners'])
    with col2:
        st.metric("Ready (Low Risk)", readiness_report['low_risk_count'], delta="✓")
    with col3:
        st.metric("At Risk (Medium)", readiness_report['medium_risk_count'], delta="⚠")
    with col4:
        st.metric("High Risk", readiness_report['high_risk_count'], delta="❌")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avg Practice Score", f"{readiness_report['average_score']:.1f}%")
    with col2:
        st.metric("Avg Study Hours", f"{readiness_report['average_study_hours']:.1f}h")
    
    # Risk Distribution Chart
    st.subheader("📈 Risk Distribution")
    
    risk_data = {
        "Risk Level": ["Low", "Medium", "High"],
        "Count": [
            readiness_report['low_risk_count'],
            readiness_report['medium_risk_count'],
            readiness_report['high_risk_count']
        ],
        "Color": ["#09ab3b", "#ff9500", "#ff2b2b"]
    }
    
    fig_risk = px.pie(
        values=risk_data["Count"],
        names=risk_data["Risk Level"],
        color_discrete_sequence=risk_data["Color"],
        title="Team Risk Distribution"
    )
    st.plotly_chart(fig_risk, use_container_width=True)
    
    # Skill Gap Analysis
    st.subheader("🔍 Skill Gap Analysis")
    
    skill_gaps = manager.identify_skill_gaps()
    
    if skill_gaps['skill_gaps']:
        gap_df = pd.DataFrame([
            {"Skill": skill, "Learners Struggling": count}
            for skill, count in skill_gaps['skill_gaps'].items()
        ])
        
        fig_skills = px.bar(
            gap_df,
            x="Skill",
            y="Learners Struggling",
            title="Skills Where Team Struggles Most",
            color="Learners Struggling",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_skills, use_container_width=True)
    
    # High Risk Employees
    st.subheader("⚠️ High Risk Employees - Intervention Needed")
    
    high_risk_data = manager.get_high_risk_employees()
    
    if high_risk_data['employees']:
        risk_df = pd.DataFrame([
            {
                "Learner ID": emp["learner_id"],
                "Practice Score": emp["practice_score"],
                "Hours Studied": emp["hours_studied"],
                "Reason": emp["reason"]
            }
            for emp in high_risk_data['employees']
        ])
        st.dataframe(risk_df, use_container_width=True)
        
        # Intervention plan
        st.subheader("📋 Recommended Interventions")
        intervention = manager.generate_intervention_plan()
        for intervention_item in intervention['interventions']:
            st.write(f"• {intervention_item}")
    else:
        st.success("✓ No high-risk employees. Team is on track!")
    
    # Performance vs Workload
    st.subheader("📊 Performance vs Workload Analysis")
    
    performance_df = pd.DataFrame(sample_learners)
    
    fig_scatter = px.scatter(
        performance_df,
        x="meeting_hours",
        y="practice_score",
        color="risk_level",
        size="hours_studied",
        hover_data=["learner_id"],
        title="Practice Score vs Meeting Hours",
        color_discrete_map={"LOW": "#09ab3b", "MEDIUM": "#ff9500", "HIGH": "#ff2b2b"},
        labels={
            "meeting_hours": "Weekly Meeting Hours",
            "practice_score": "Practice Score (%)"
        }
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Learner Details Table
    st.subheader("📋 Detailed Learner Data")
    st.dataframe(performance_df, use_container_width=True)


def main():
    """Main app router"""
    st.sidebar.title("🎯 CertPilot")
    st.sidebar.markdown("Certification Success Platform")
    
    # Initialize session state
    if "employee_generated" not in st.session_state:
        st.session_state.employee_generated = False
    
    page = st.sidebar.radio(
        "Select View",
        ["Employee View", "Manager View"]
    )
    
    st.sidebar.divider()
    st.sidebar.markdown("### 📊 About CertPilot")
    st.sidebar.info(
        """
        **CertPilot** uses advanced AI agents to:
        
        ✅ Curate personalized learning paths  
        📅 Create realistic study schedules  
        ⚖️ Analyze work-life balance (Work IQ)  
        📝 Assess knowledge gaps  
        🔮 Predict certification success  
        👔 Provide team insights  
        ✓ Validate plans and readiness
        """
    )
    
    if page == "Employee View":
        employee_view()
    else:
        manager_view()


if __name__ == "__main__":
    main()
