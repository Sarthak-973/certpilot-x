"""
Agent 4: Assessment Agent
Purpose: Evaluates learner knowledge and identifies gaps
Output: Practice questions, weak areas, readiness score
"""

class AssessmentAgent:
    """
    Generates assessments and identifies knowledge gaps
    """
    
    def __init__(self):
        self.question_bank = [
            {
                "id": "Q001",
                "topic": "Azure Data Factory",
                "difficulty": "medium",
                "question": "What is the primary purpose of Azure Data Factory?",
                "answer": "Orchestrate data movement and transformation"
            },
            {
                "id": "Q002",
                "topic": "Synapse Analytics",
                "difficulty": "hard",
                "question": "How do you optimize query performance in Synapse?",
                "answer": "Use distribution and indexing strategies"
            }
        ]
    
    def generate_practice_questions(self, topic=None, difficulty="mixed", count=5):
        """
        Generate practice questions for the learner
        """
        questions = []
        for i, q in enumerate(self.question_bank[:count]):
            if topic is None or q["topic"] == topic:
                questions.append({
                    "number": i + 1,
                    "question": q["question"],
                    "topic": q["topic"],
                    "difficulty": q["difficulty"]
                })
        return questions
    
    def assess_knowledge(self, responses):
        """
        Assess responses and identify weak areas
        
        Args:
            responses: List of learner responses
        """
        correct = sum(1 for r in responses if r.get("correct", False))
        total = len(responses)
        score = (correct / total * 100) if total > 0 else 0
        
        weak_areas = self._identify_weak_areas(responses)
        
        return {
            "score": round(score, 1),
            "correct_answers": correct,
            "total_questions": total,
            "weak_areas": weak_areas,
            "readiness_score": self._calculate_readiness(score)
        }
    
    def _identify_weak_areas(self, responses):
        """Identify topics where learner struggles"""
        weak_topics = []
        for r in responses:
            if not r.get("correct", False):
                weak_topics.append(r.get("topic", "Unknown"))
        return list(set(weak_topics))
    
    def _calculate_readiness(self, score):
        """Calculate exam readiness based on score"""
        if score >= 80:
            return "Ready for exam"
        elif score >= 70:
            return "Mostly ready - review weak areas"
        else:
            return "Not ready - more study needed"
