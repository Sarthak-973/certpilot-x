"""
Orchestrator: Main Workflow
Purpose: Coordinates all agents in sequence
Flow:
User → Curator → Planner → Engagement → Assessment → Predictor → Critic → Final Recommendation
"""

from agents.curator_agent import CuratorAgent
from agents.planner_agent import PlannerAgent
from agents.engagement_agent import EngagementAgent
from agents.assessment_agent import AssessmentAgent
from agents.predictor_agent import PredictorAgent
from agents.manager_agent import ManagerAgent
from agents.critic_agent import CriticAgent


class CertPilotOrchestrator:
    """
    Main orchestrator that coordinates all agents in the certification workflow
    """
    
    def __init__(self):
        self.curator = CuratorAgent()
        self.planner = PlannerAgent()
        self.engagement = EngagementAgent()
        self.assessment = AssessmentAgent()
        self.predictor = PredictorAgent()
        self.manager = ManagerAgent()
        self.critic = CriticAgent()
        
        self.workflow_state = {}
    
    def execute_workflow(self, user_input):
        """
        Execute complete certification workflow
        
        Args:
            user_input: dict with user details
                {
                    "learner_id": "L1001",
                    "role": "Data Engineer",
                    "exam_date": "2026-07-15",
                    "hours_per_week": 5,
                    "meeting_hours": 20,
                    "focus_hours": 12
                }
        """
        print("\n" + "="*60)
        print("CERTPILOT WORKFLOW EXECUTION")
        print("="*60)
        
        # Step 1: CURATOR - Create learning path
        print("\n[1/7] CURATOR AGENT: Building Learning Path...")
        curator_output = self.curator.curate_learning_path(user_input.get("role", "Data Engineer"))
        self.workflow_state["curator"] = curator_output
        print(f"✓ Certification Path: {curator_output.get('certification')}")
        print(f"✓ Skills: {', '.join(curator_output.get('skills', []))}")
        
        # Step 2: PLANNER - Create study schedule
        print("\n[2/7] PLANNER AGENT: Creating Study Schedule...")
        planner_output = self.planner.create_study_plan(
            hours_per_week=user_input.get("hours_per_week", 5),
            exam_date=user_input.get("exam_date", "2026-07-15")
        )
        self.workflow_state["planner"] = planner_output
        print(f"✓ Study Plan Created: {planner_output['total_weeks']} weeks")
        print(f"✓ Hours per week: {planner_output['hours_per_week']}")
        
        # Step 3: ENGAGEMENT - Analyze workload
        print("\n[3/7] ENGAGEMENT AGENT: Analyzing Work-Life Balance (Work IQ)...")
        engagement_output = self.engagement.analyze_workload(
            meeting_hours=user_input.get("meeting_hours", 20),
            focus_hours=user_input.get("focus_hours", 12)
        )
        self.workflow_state["engagement"] = engagement_output
        print(f"✓ Risk Level: {engagement_output['risk_level']}")
        print(f"✓ Study Window: {self.engagement.find_study_window(engagement_output['meeting_hours'])}")
        print(f"✓ Recommendation: {engagement_output['recommendation']}")
        
        # Step 4: ASSESSMENT - Evaluate current knowledge
        print("\n[4/7] ASSESSMENT AGENT: Generating Practice Assessment...")
        practice_questions = self.assessment.generate_practice_questions(count=3)
        self.workflow_state["assessment"] = {
            "questions": practice_questions,
            "mock_responses": [
                {"correct": True, "topic": "Azure Data Factory"},
                {"correct": False, "topic": "Synapse Analytics"},
                {"correct": True, "topic": "Data Storage"}
            ]
        }
        assessment_result = self.assessment.assess_knowledge(
            self.workflow_state["assessment"]["mock_responses"]
        )
        self.workflow_state["assessment"]["result"] = assessment_result
        print(f"✓ Practice Score: {assessment_result['score']}%")
        print(f"✓ Weak Areas: {', '.join(assessment_result['weak_areas']) if assessment_result['weak_areas'] else 'None'}")
        print(f"✓ Readiness: {assessment_result['readiness_score']}")
        
        # Step 5: PREDICTOR - Predict success (DIFFERENTIATOR)
        print("\n[5/7] PREDICTOR AGENT: Calculating Pass Probability (CertPilot Differentiator)...")
        predictor_output = self.predictor.predict_pass_probability(
            practice_score=assessment_result['score'],
            study_hours=user_input.get("hours_per_week", 5) * 4,  # Assume 4 weeks so far
            meeting_hours=user_input.get("meeting_hours", 20)
        )
        self.workflow_state["predictor"] = predictor_output
        print(f"✓ Pass Probability: {predictor_output['pass_probability']}%")
        print(f"✓ Risk Level: {predictor_output['risk_level']}")
        print(f"✓ Recommendation: {predictor_output['recommendation']}")
        
        # Step 6: CRITIC - Validate everything
        print("\n[6/7] CRITIC AGENT: Validating Plan & Readiness...")
        critic_output = self.critic.validate_study_plan(planner_output)
        self.workflow_state["critic"] = critic_output
        print(f"✓ Plan Valid: {critic_output['is_valid']}")
        if critic_output['warnings']:
            for warning in critic_output['warnings']:
                print(f"  ⚠ {warning}")
        if critic_output['errors']:
            for error in critic_output['errors']:
                print(f"  ✗ {error}")
        
        readiness_check = self.critic.verify_readiness_criteria({
            "practice_score": assessment_result['score'],
            "hours_studied": user_input.get("hours_per_week", 5) * 4,
            "weak_areas": assessment_result['weak_areas']
        })
        print(f"✓ Readiness Assessment: {readiness_check['recommendation']}")
        
        # Step 7: FINAL RECOMMENDATION
        print("\n[7/7] FINAL RECOMMENDATION")
        print("="*60)
        final_recommendation = self._generate_final_recommendation(user_input)
        print(final_recommendation)
        
        return {
            "learner_id": user_input.get("learner_id"),
            "workflow_state": self.workflow_state,
            "final_recommendation": final_recommendation
        }
    
    def _generate_final_recommendation(self, user_input):
        """Generate final recommendation based on workflow"""
        recommendation = "\n🎯 PERSONALIZED CERTIFICATION ROADMAP\n"
        recommendation += "-" * 60 + "\n"
        
        cert = self.workflow_state["curator"].get("certification", "DP-203")
        recommendation += f"Certification Target: {cert}\n"
        recommendation += f"Learner: {user_input.get('learner_id', 'Unknown')}\n"
        recommendation += f"Study Plan: {self.workflow_state['planner']['total_weeks']} weeks\n"
        recommendation += f"Predicted Success Rate: {self.workflow_state['predictor']['pass_probability']}%\n"
        recommendation += f"Risk Assessment: {self.workflow_state['predictor']['risk_level']}\n\n"
        
        recommendation += "📋 NEXT STEPS:\n"
        recommendation += f"1. {self.workflow_state['engagement']['recommendation']}\n"
        recommendation += f"2. Study window: {self.engagement.find_study_window(self.workflow_state['engagement']['meeting_hours'])}\n"
        recommendation += f"3. Focus on weak areas: {', '.join(self.workflow_state['assessment']['result']['weak_areas']) or 'None identified'}\n"
        recommendation += f"4. {self.workflow_state['predictor']['recommendation']}\n"
        
        recommendation += "\n⚠️  VALIDATION NOTES:\n"
        if self.workflow_state['critic']['is_valid']:
            recommendation += "✓ Study plan is realistic and achievable\n"
        else:
            recommendation += "✗ Plan needs adjustment\n"
        
        recommendation += "\n✨ This personalized roadmap combines Work IQ analysis, predictive modeling,\n"
        recommendation += "   and expert validation to maximize your certification success.\n"
        
        return recommendation


def main():
    """Demo execution"""
    orchestrator = CertPilotOrchestrator()
    
    user_data = {
        "learner_id": "L1001",
        "role": "Data Engineer",
        "exam_date": "2026-07-15",
        "hours_per_week": 5,
        "meeting_hours": 20,
        "focus_hours": 12
    }
    
    result = orchestrator.execute_workflow(user_data)
    
    return result


if __name__ == "__main__":
    main()
