import datetime

class SharedMemory:
    def __init__(self):
        self.messages = []
        self.requirements = []
        self.issues = []
        self.clarifications = []
        self.message_id = 1

    def write(self, name: str, message: str, turn: int, role: str = "agent"):
        self.messages.append({
            "turn": turn,
            "id": self.message_id,
            "agent": name,
            "role": role,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat()
            })
        self.message_id += 1
        
    def read(self):
        print("[SharedMemory] Reading the latest message")
        if len(self.messages) == 0:
            return None
        print(f"[SharedMemory] Latest message: {self.messages[-1]}\n\n")
        return self.messages[-1]

    def get_all_messages(self):
        print(f"[SharedMemory] Reading {len(self.messages)} messages")
        return self.messages
    
    def get_requirements(self):
        print(f"[SharedMemory] Reading {len(self.requirements)} requirements")
        return self.requirements
    
    def get_issues(self):
        print(f"[SharedMemory] Reading {len(self.issues)} issues")
        return self.issues
    
    def get_clarifications(self):
        print(f"[SharedMemory] Reading {len(self.clarifications)} clarifications")
        return self.clarifications


    def save_requirements(self, stakeholder_name, trace_message_id, turn_id, requirements):
        requirements = requirements
        for req in requirements:
            self.requirements.append({
                "req_id": len(self.requirements) + 1,
                "turn_id": turn_id,
                "createdBy": stakeholder_name,
                "trace_message_id": trace_message_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "requirement": req
        })
        print(f"[SharedMemory] Saved {len(requirements)} requirements")

    def save_issues(self, stakeholder_name, trace_message_id, turn_id, issues):
        issues = issues
        for issue in issues:
            self.issues.append({
                "issue_id": len(self.issues) + 1,
                "trace_message_id": trace_message_id,
                "createdBy": stakeholder_name,
                "turn_id": turn_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "issue": issue
        })
            
        """for clarification in clarifications:
            self.clarifications.append({
                "clarification_id": len(self.clarifications) + 1,
                "trace_message_id": trace_message_id,
                "createdBy": stakeholder_name,
                "turn_id": turn_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "clarification": clarification
        })"""
        print(f"[SharedMemory] Saved {len(issues)} issues")