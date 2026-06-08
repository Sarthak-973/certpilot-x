"""
Agent 2: Study Planner
Purpose: Creates structured study schedule based on timeline
Input: Hours per week, Exam date
Output: Week-by-week learning plan
"""

from datetime import datetime, timedelta

class PlannerAgent:
    """
    Creates detailed week-by-week study schedule
    """
    
    def __init__(self):
        self.weeks_data = {}
    
    def create_study_plan(self, hours_per_week, exam_date, total_hours=25):
        """
        Generate week-by-week study plan
        
        Args:
            hours_per_week: Study hours available per week
            exam_date: Target exam date
            total_hours: Total recommended study hours
        """
        exam_dt = datetime.strptime(exam_date, "%Y-%m-%d")
        today = datetime.now()
        weeks_available = (exam_dt - today).days / 7
        
        weeks_per_topic = total_hours / hours_per_week
        
        plan = {
            "total_weeks": int(weeks_available),
            "hours_per_week": hours_per_week,
            "exam_date": exam_date,
            "weekly_schedule": []
        }
        
        topics = [
            "Azure Data Factory Fundamentals",
            "Synapse Analytics Deep Dive",
            "Data Storage Solutions",
            "Practice Questions & Review"
        ]
        
        for week_num in range(1, int(weeks_available) + 1):
            topic_idx = min(week_num - 1, len(topics) - 1)
            plan["weekly_schedule"].append({
                "week": week_num,
                "topic": topics[topic_idx],
                "hours": hours_per_week,
                "milestones": ["Complete readings", "Do hands-on lab", "Review notes"]
            })
        
        return plan
    
    def adjust_pace(self, progress_percentage):
        """Adjust study pace based on progress"""
        if progress_percentage < 50:
            return "Accelerate: You're behind schedule"
        elif progress_percentage > 100:
            return "Can slow down: You're ahead"
        else:
            return "On track: Maintain current pace"
