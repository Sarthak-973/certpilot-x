"""
Agent 6: Manager Agent
Purpose: Provides team-level insights and management view
Output: Team Readiness, Skill Gaps, High Risk Employees
"""

class ManagerAgent:
    """
    Aggregates learner data for manager insights and decisions
    """
    
    def __init__(self):
        self.learners = []
    
    def add_learner_data(self, learner):
        """Add learner data to manager's view"""
        self.learners.append(learner)
    
    def generate_team_readiness_report(self):
        """
        Generate comprehensive team readiness report
        """
        if not self.learners:
            return {"error": "No learner data available"}
        
        high_risk = [l for l in self.learners if l.get("risk_level") == "HIGH"]
        medium_risk = [l for l in self.learners if l.get("risk_level") == "MEDIUM"]
        low_risk = [l for l in self.learners if l.get("risk_level") == "LOW"]
        
        avg_score = sum(l.get("practice_score", 0) for l in self.learners) / len(self.learners)
        avg_study_hours = sum(l.get("hours_studied", 0) for l in self.learners) / len(self.learners)
        
        return {
            "total_learners": len(self.learners),
            "low_risk_count": len(low_risk),
            "medium_risk_count": len(medium_risk),
            "high_risk_count": len(high_risk),
            "average_score": round(avg_score, 1),
            "average_study_hours": round(avg_study_hours, 1),
            "team_readiness": self._calculate_team_readiness(low_risk, medium_risk, high_risk)
        }
    
    def identify_skill_gaps(self):
        """Identify team-wide skill gaps"""
        skill_gaps = {}
        for learner in self.learners:
            weak_areas = learner.get("weak_areas", [])
            for area in weak_areas:
                skill_gaps[area] = skill_gaps.get(area, 0) + 1
        
        return {
            "skill_gaps": skill_gaps,
            "most_common_gap": max(skill_gaps, key=skill_gaps.get) if skill_gaps else "None"
        }
    
    def get_high_risk_employees(self):
        """Get list of employees at high risk of failing"""
        high_risk = [l for l in self.learners if l.get("risk_level") == "HIGH"]
        return {
            "count": len(high_risk),
            "employees": [
                {
                    "learner_id": l.get("learner_id"),
                    "practice_score": l.get("practice_score"),
                    "hours_studied": l.get("hours_studied"),
                    "reason": self._explain_risk(l)
                }
                for l in high_risk
            ]
        }
    
    def _calculate_team_readiness(self, low, medium, high):
        """Calculate overall team readiness percentage"""
        total = len(low) + len(medium) + len(high)
        if total == 0:
            return 0
        readiness = (len(low) * 100 + len(medium) * 50 + len(high) * 0) / total
        return round(readiness, 1)
    
    def _explain_risk(self, learner):
        """Explain why learner is at risk"""
        reasons = []
        if learner.get("practice_score", 0) < 70:
            reasons.append("Low practice score")
        if learner.get("hours_studied", 0) < 15:
            reasons.append("Insufficient study time")
        return "; ".join(reasons) if reasons else "Other factors"
    
    def generate_intervention_plan(self):
        """Generate intervention plan for at-risk learners"""
        high_risk = self.get_high_risk_employees()
        return {
            "target_learners": high_risk["count"],
            "interventions": [
                "Schedule 1-on-1 tutoring sessions",
                "Provide additional practice materials",
                "Consider exam postponement",
                "Assign peer mentors"
            ],
            "timeline": "Within 1 week"
        }
