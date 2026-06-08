"""
Agent 5: Predictor Agent (DIFFERENTIATOR)
Purpose: Predicts certification pass probability
This is the unique agent that sets CertPilot apart.
Input: Practice Score, Study Hours, Meeting Hours
Output: Pass Probability, Risk Level
"""

class PredictorAgent:
    """
    Predicts certification success using historical patterns.
    This is the differentiating feature of CertPilot.
    """
    
    def __init__(self):
        self.pass_threshold = 75
        self.historical_data = {
            "high_study_low_meetings": {"pass_rate": 0.92, "risk": "LOW"},
            "medium_study_medium_meetings": {"pass_rate": 0.78, "risk": "MEDIUM"},
            "low_study_high_meetings": {"pass_rate": 0.45, "risk": "HIGH"}
        }
    
    def predict_pass_probability(self, practice_score, study_hours, meeting_hours):
        """
        Predict certification pass probability using ML-like logic
        
        Args:
            practice_score: Average practice test score (0-100)
            study_hours: Total hours studied so far
            meeting_hours: Weekly meeting hours
        
        Returns:
            dict with pass_probability and risk_level
        """
        # Weighted calculation
        score_weight = practice_score * 0.5
        study_weight = min(study_hours / 25, 1.0) * 100 * 0.3  # Normalized to 25 recommended hours
        meeting_penalty = max(0, 1 - (meeting_hours / 40)) * 100 * 0.2  # Penalty for high meetings
        
        pass_probability = (score_weight + study_weight + meeting_penalty) / 100
        pass_probability = min(max(pass_probability, 0), 1)  # Clamp between 0 and 1
        
        risk_level = self._calculate_risk_level(pass_probability, practice_score, meeting_hours)
        
        return {
            "pass_probability": round(pass_probability * 100, 1),
            "pass_threshold": self.pass_threshold,
            "predicted_score": round(practice_score * pass_probability, 1),
            "risk_level": risk_level,
            "recommendation": self._get_recommendation(pass_probability, practice_score)
        }
    
    def _calculate_risk_level(self, probability, score, meetings):
        """Calculate risk classification"""
        if probability >= 0.8:
            return "LOW"
        elif probability >= 0.6:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _get_recommendation(self, probability, score):
        """Generate specific recommendations"""
        if probability >= 0.8:
            return "On track for success. Maintain current study pace."
        elif probability >= 0.6:
            return "Doable but risky. Increase study hours and review weak areas."
        else:
            return "High risk. Recommend intensive tutoring or exam delay."
    
    def predict_team_pass_rate(self, learners_data):
        """
        Predict overall team pass rate
        
        Args:
            learners_data: List of learner prediction data
        """
        if not learners_data:
            return 0.0
        
        total_probability = sum(learner.get("pass_probability", 0) for learner in learners_data)
        avg_probability = total_probability / len(learners_data)
        
        return {
            "team_pass_rate": round(avg_probability, 1),
            "learners_at_risk": sum(1 for l in learners_data if l.get("risk_level") == "HIGH"),
            "learners_ready": sum(1 for l in learners_data if l.get("risk_level") == "LOW")
        }
