from .base_agent import BaseAgent

class HelperAgent(BaseAgent):
    def speak(self, message, type, existing_requirements=None, existing_issues=None):
        system_context = f"Project: {self.description}\n\n"

        prompt = ""
        if type == "REQUIREMENT":
            prompt = self.requirementExtraction(message, existing_requirements)
        elif type == "ISSUE":
            prompt = self.issueExtraction(message, existing_requirements, existing_issues)

        final_prompt = system_context + prompt
        print(f"[Analyst Agent Prompt]: Analyzing stakeholder statement for {type} extraction...")
        
        response = self.agent.invoke(final_prompt)

        if response and response.content:
            response = response.content.strip()
        
        return response
    
    def requirementExtraction(self, message, existing_requirements=None):
        existing_context = ""
        if existing_requirements and len(existing_requirements) > 0:
            existing_context = (
                "Already Extracted Requirements (DO NOT re-extract these)\n"
                f"{existing_requirements}\n\n"
            )

        return f"""
            You are a Requirements Extraction Specialist.

            Extract requirements ONLY from the stakeholder statement below.

            {existing_context}HARD RULES:
            1) Extract ONLY from stakeholder statements.
            2) DO NOT invent numbers, metrics, policies, or performance targets.
            3) "description" MUST contain a clear summary of what the stakeholder needs. This field must NEVER be empty or blank.
            4) "evidence_quote" MUST be a SHORT phrase (under 20 words) copied exactly from the statement.
            5) If a requirement is implied (e.g., 'manual and time-consuming'), set needs_clarification=true and add specific questions.
            6) Do NOT re-extract requirements that already exist above.
            7) If the statement contains NO new requirements, return: {{ "requirements": [] }}

            OUTPUT ONLY VALID JSON WITH THIS EXACT STRUCTURE AND NO OTHER TEXT:
            {{
                "requirements": [
                    {{
                        "type": "functional|non-functional",
                        "description": "<REQUIRED: clear summary of what the stakeholder needs>",
                        "needs_clarification": true,
                        "questions": ["<specific clarification question>"],
                        "evidence_quote": "<short exact phrase from the statement>",
                    }}
                ]
            }}

            If none found: {{ "requirements": [] }}

            REMINDER: Output ONLY the JSON object. No explanations, no preamble, no markdown fences.\n

            Stakeholder statement:
            \"\"\"{message}\"\"\"
        """.strip()


    def issueExtraction(self, message, existing_requirements=None, existing_issues=None):
        req_context = ""
        if existing_requirements:
            req_context = f"Existing Requirements for Reference\n{existing_requirements}\n\n"

        issues_context = ""
        if existing_issues and len(existing_issues) > 0:
            issues_context = (
                "Already Extracted Issues (DO NOT re-extract these)\n"
                f"{existing_issues}\n\n"
            )

        return f"""
            You are an Issues Detection Specialist.

            {req_context}{issues_context}Extract issues ONLY if explicitly indicated by the stakeholder statement.
            Do NOT add generic risks (privacy, misuse, scalability) unless mentioned.

            HARD RULES:
            1) Extract ONLY from stakeholder statements.
            2) "description" MUST clearly describe the issue. This field must NEVER be empty or blank.
            3) "evidence_quote" MUST be a SHORT phrase copied exactly from the statement.
            4) Do NOT re-extract issues that already exist above.
            5) If the statement contains NO new issues, return: {{ "issues": [] }}

            OUTPUT ONLY VALID JSON WITH THIS EXACT STRUCTURE AND NO OTHER TEXT:
            {{
                "issues": [
                    {{
                        "type": "conflict|ambiguity|risk|blocker|concern|process_gap",
                        "description": "<REQUIRED: clear description of the issue>",
                        "severity": "high|medium|low",
                        "status": "open",
                        "related_requirement_id": "<taken from req_id or empty string>",
                        "evidence_quote": "<short exact phrase from the statement>"
                    }}
                ]
            }}

            If none found: {{ "issues": [] }}

            REMINDER: Output ONLY the JSON object. No explanations, no preamble, no markdown fences.\n

            Stakeholder statement:
            \"\"\"{message}\"\"\"
        """.strip()