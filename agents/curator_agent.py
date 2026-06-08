"""
Agent 1: Learning Curator
Purpose: Maps role to certification path, skills, and resources
"""

class CuratorAgent:
    """
    Transforms role into structured learning path.
    Role → Certification Path → Skills → Resources
    """
    
    def __init__(self):
        self.role_mappings = {
            "Data Engineer": {
                "certification": "DP-203",
                "skills": [
                    "Azure Data Factory",
                    "Synapse Analytics",
                    "Data Storage"
                ],
                "resources": [
                    "Microsoft Learn modules",
                    "Practice labs",
                    "Documentation"
                ]
            }
        }
    
    def curate_learning_path(self, role):
        """
        Curate personalized learning path based on role
        """
        if role in self.role_mappings:
            path = self.role_mappings[role]
            return {
                "role": role,
                "certification": path["certification"],
                "skills": path["skills"],
                "resources": path["resources"],
                "status": "Path created"
            }
        return {"error": "Role not found"}
    
    def get_skill_details(self, skill):
        """Get detailed information about a skill"""
        return {
            "skill": skill,
            "duration": "variable",
            "difficulty": "intermediate",
            "prerequisites": []
        }
