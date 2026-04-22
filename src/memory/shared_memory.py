import datetime

class SharedMemory:
    def __init__(self):
        self.messages = []
        self.requirements = []
        self.issues = []
        self.clarifications = []
        self.message_id = 1

    def write(self, name: str, message: str, turn: int, role: str = "agent"):
        saved_id = self.message_id
        self.messages.append({
            "turn": turn,
            "id": saved_id,
            "agent": name,
            "role": role,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat()
            })
        
        print(f"[SharedMemory] Saved messages from {name} at turn {turn} with id {saved_id}")
        self.message_id += 1

        return saved_id
        
    def read(self):
        print("[SharedMemory] Reading the latest message")
        if len(self.messages) == 0:
            return None
        
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
    
    def get_requirements_formatted(self):
        if not self.requirements:
            return ""
        lines = []
        for req in self.requirements:
            req_id = req.get("req_id", "?")
            nested = req.get("requirement", {})
            desc = (
                nested.get("description")
                or req.get("description", "")
            )
            lines.append(f"  [{req_id}] {desc}")
        return "\n".join(lines)

    def get_issues_formatted(self):
        if not self.issues:
            return ""
        lines = []
        for iss in self.issues:
            iss_id = iss.get("issue_id", "?")
            nested = iss.get("issue", {})
            desc = nested.get("description") or iss.get("description", "")
            iss_type = nested.get("type") or iss.get("type", "")
            lines.append(f"  [{iss_id}] ({iss_type}) {desc}")
        return "\n".join(lines)
    
    def get_messages_formatted(self, *, exclude_last: bool = False):
        if not self.messages:
            return ""

        messages = self.messages[:-1] if exclude_last else self.messages
        if not messages:
            return ""

        lines = []
        for msg in messages:
            agent = msg.get("agent", "Unknown")
            turn = msg.get("turn", "?")
            text = msg.get("message", "")
            lines.append(f"  [Turn {turn}] {agent}: {text}")
        return "\n".join(lines)

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
    
    def resolve_requirement(self, req_id, confirmed_by_turn):
        for req in self.requirements:
            if req["req_id"] == req_id:
                req["requirement"]["needs_clarification"] = False
                req["resolved_by_turn"] = confirmed_by_turn
                print(f"[SharedMemory] Resolved requirement {req_id} at turn {confirmed_by_turn}")

    def save_issues(self, stakeholder_name, trace_message_id, turn_id, issues):
        issues = issues
        for issue in issues:
            typeCheck = issue.get("related_requirement_id")
            if typeCheck is not None and typeCheck != "none":
                issue["related_requirement_id"] = int(issue.get("related_requirement_id"))

            self.issues.append({
                "issue_id": len(self.issues) + 1,
                "trace_message_id": trace_message_id,
                "createdBy": stakeholder_name,
                "turn_id": turn_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "issue": issue
        })
            
        print(f"[SharedMemory] Saved {len(issues)} issues")