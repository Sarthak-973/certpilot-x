"""
Agent 7: Critic Agent (Verifier)
Purpose: Validates study plans and identifies unrealistic scenarios
This demonstrates the Critic/Verifier pattern mentioned in the challenge.
"""

class CriticAgent:
    """
    Validates and critiques study plans, identifies risks.
    The Critic pattern: Challenge assumptions and verify feasibility.
    """
    
    def __init__(self):
        self.min_study_hours = 20
        self.max_weekly_hours = 40
        self.pass_threshold = 75
    
    def validate_study_plan(self, plan):
        """
        Validate study plan for feasibility and completeness
        
        Args:
            plan: Study plan dict with schedule and targets
        """
        issues = []
        warnings = []
        
        # Check if plan has required hours
        if plan.get("total_weeks", 0) == 0:
            issues.append("ERROR: No study weeks in plan")
        
        total_hours = plan.get("hours_per_week", 0) * plan.get("total_weeks", 0)
        if total_hours < self.min_study_hours:
            issues.append(f"ERROR: Total study hours ({total_hours}) below minimum ({self.min_study_hours})")
        
        if plan.get("hours_per_week", 0) > self.max_weekly_hours:
            warnings.append(f"WARNING: {plan['hours_per_week']} hours/week exceeds recommended maximum")
        
        if not plan.get("weekly_schedule"):
            issues.append("ERROR: No weekly schedule defined")
        
        return {
            "is_valid": len(issues) == 0,
            "errors": issues,
            "warnings": warnings,
            "plan_quality": self._assess_plan_quality(plan)
        }
    
    def check_prerequisites(self, learner, certification):
        """
        Verify learner meets prerequisites
        """
        missing_prereqs = []
        
        # Example prerequisite checking
        required_skills = ["Basic Azure", "SQL Fundamentals"]
        learner_skills = learner.get("skills", [])
        
        for skill in required_skills:
            if skill not in learner_skills:
                missing_prereqs.append(skill)
        
        return {
            "prerequisites_met": len(missing_prereqs) == 0,
            "missing_prerequisites": missing_prereqs,
            "recommendation": "Complete prerequisites first" if missing_prereqs else "Ready to proceed"
        }
    
    def detect_unrealistic_schedules(self, hours_per_week, meeting_hours, availability):
        """
        Detect if study schedule is unrealistic given constraints
        """
        issues = []
        
        # Logic to detect unrealistic scenarios
        if hours_per_week + meeting_hours > self.max_weekly_hours:
            issues.append(f"UNREALISTIC: Total commitment ({hours_per_week + meeting_hours}h) exceeds 40h/week")
        
        if hours_per_week > 15 and meeting_hours > 20:
            issues.append("UNREALISTIC: Very high study hours combined with heavy meeting load")
        
        # Check early morning expectations
        if hours_per_week > 20 and availability == "Morning only":
            issues.append("UNREALISTIC: Cannot fit {hours_per_week} hours in morning slots only")
        
        return {
            "is_realistic": len(issues) == 0,
            "detected_issues": issues,
            "feasibility_rating": "High" if len(issues) == 0 else "Low"
        }
    
    def verify_readiness_criteria(self, learner_data):
        """
        Verify if learner meets readiness criteria for exam
        """
        criteria_met = []
        criteria_failed = []
        
        # Practice score >= 75
        if learner_data.get("practice_score", 0) >= 75:
            criteria_met.append("Practice score >= 75")
        else:
            criteria_failed.append(f"Practice score {learner_data.get('practice_score', 0)} < 75")
        
        # Study hours >= recommended
        recommended_hours = 25
        if learner_data.get("hours_studied", 0) >= recommended_hours:
            criteria_met.append(f"Study hours >= {recommended_hours}")
        else:
            criteria_failed.append(f"Study hours {learner_data.get('hours_studied', 0)} < {recommended_hours}")
        
        # No critical weak areas
        weak_areas = learner_data.get("weak_areas", [])
        if not weak_areas:
            criteria_met.append("No critical weak areas")
        else:
            criteria_failed.append(f"Weak areas identified: {', '.join(weak_areas)}")
        
        return {
            "ready_for_exam": len(criteria_failed) == 0,
            "criteria_met": criteria_met,
            "criteria_failed": criteria_failed,
            "recommendation": "Ready to take exam" if len(criteria_failed) == 0 else "Not ready - address issues first"
        }
    
    def _assess_plan_quality(self, plan):
        """Assess overall quality of plan"""
        quality_score = 0
        
        if plan.get("total_weeks"):
            quality_score += 20
        if plan.get("hours_per_week"):
            quality_score += 20
        if plan.get("weekly_schedule") and len(plan["weekly_schedule"]) > 0:
            quality_score += 30
        if plan.get("exam_date"):
            quality_score += 30
        
        return round(quality_score, 0)
