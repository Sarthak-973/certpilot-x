"""
Agent 3: Engagement Agent (Work IQ)
Purpose: Analyzes workload and optimizes study windows
Input: Meeting hours, Focus hours
Output: Best study window and recommendations
"""

class EngagementAgent:
    """
    Analyzes work patterns to find optimal study windows.
    Demonstrates Work IQ reasoning.
    """
    
    def __init__(self):
        self.time_slots = {
            "Morning": {"hours": 3, "quality": "high"},
            "Afternoon": {"hours": 4, "quality": "medium"},
            "Evening": {"hours": 2, "quality": "low"}
        }
    
    def analyze_workload(self, meeting_hours, focus_hours):
        """
        Analyze employee workload and recommend study strategy
        
        Args:
            meeting_hours: Hours spent in meetings per week
            focus_hours: Hours of focused work per week
        """
        total_work_hours = meeting_hours + focus_hours
        
        # Work IQ logic
        if meeting_hours > 20:
            risk_level = "HIGH"
            recommendation = "Very limited study time available"
        elif meeting_hours > 15:
            risk_level = "MEDIUM"
            recommendation = "Moderate study challenges"
        else:
            risk_level = "LOW"
            recommendation = "Good time availability for study"
        
        return {
            "meeting_hours": meeting_hours,
            "focus_hours": focus_hours,
            "total_work_hours": total_work_hours,
            "risk_level": risk_level,
            "recommendation": recommendation
        }
    
    def find_study_window(self, meeting_hours):
        """Find optimal study time based on meeting load"""
        if meeting_hours <= 10:
            return "Morning or Afternoon"
        elif meeting_hours <= 20:
            return "Early Morning (6-8 AM)"
        else:
            return "Weekend or Late Evening"
    
    def calculate_study_hours(self, available_hours_per_day, days_per_week):
        """Calculate achievable weekly study hours"""
        total_hours = available_hours_per_day * days_per_week
        return {
            "daily_hours": available_hours_per_day,
            "days_per_week": days_per_week,
            "total_weekly_hours": total_hours,
            "feasibility": "High" if total_hours >= 10 else "Low"
        }
