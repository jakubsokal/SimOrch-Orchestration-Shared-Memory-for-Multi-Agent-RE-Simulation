from .base_agent import BaseAgent

class HelperAgent(BaseAgent):
    def speak(self, message, type, existing_requirements=None, existing_issues=None, corrections=None, missed_items=None):
        system_context = f"Project: {self.description}\n\n"

        prompt = ""
        if type == "REQUIREMENT":
            prompt = self.requirement_extraction(message, existing_requirements)
        elif type == "ISSUE":
            prompt = self.issue_extraction(message, existing_requirements, existing_issues)
        elif type == "REQUIREMENT_CORRECTION":
            prompt = self.requirement_correction(message, existing_requirements, corrections, missed_items)
        elif type == "ISSUE_CORRECTION":
            prompt = self.issue_correction(message, existing_requirements, existing_issues, corrections, missed_items)

        final_prompt = system_context + prompt
        print(f"[Analyst Agent Prompt]: Analyzing stakeholder statement for {type} extraction...")
        
        response = self.agent.invoke(final_prompt)

        response_text = self.get_response(response)
        if response_text is not None:
            response_text = str(response_text).strip()
        return response_text

    
    def requirement_extraction(self, message, existing_requirements=None):
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
            4) "evidence_quote" MUST be a SHORT phrase (under 50 words) copied exactly from the statement.
            5) If a requirement is implied OR expressed with uncertain language 
            (e.g. 'I think', 'would be helpful', 'would be beneficial', 'might be useful', 
            'could potentially'), set needs_clarification=true and add a question asking 
            the stakeholder to confirm whether this is a firm requirement.
            6) Do NOT re-extract requirements that already exist above.
            7) If the statement contains NO new requirements, return: {{ "requirements": [] }}
            8) Extract at most ONE requirement per distinct stakeholder NEED, not 
            per sentence. If a stakeholder describes several aspects of the same 
            need (e.g. multiple UI features that all serve "usability"), group 
            them into one requirement with a comprehensive description rather 
            than extracting a separate requirement per sentence.
            Ask yourself: "Are these separate system capabilities, or aspects 
            of the same capability?" If the same, merge them.
            9) For "type" classification:
            - "functional": describes something the system DOES - a feature, 
                behaviour, or action (book a room, send a notification, filter results)
            - "non-functional": describes a QUALITY of how the system does it - 
                performance, usability, reliability, accessibility, security
            Examples of non-functional: response time, interface clarity, 
            accessibility for non-technical users, number of clicks, uptime.
            When in doubt: if removing the requirement would reduce WHAT the 
            system does, it is functional. If it would only reduce HOW WELL 
            the system does it, it is non-functional.
            10) Before extracting any requirement, check the Already Extracted 
            Requirements list above. If the new requirement describes the same 
            capability as an existing one - even if the stakeholder is providing 
            more detail or confirming it - do NOT re-extract it. 
            Return {{ "requirements": [], "resolves_req_id": <req_id> }} instead.

            OUTPUT ONLY VALID JSON WITH THIS EXACT STRUCTURE AND NO OTHER TEXT:
            {{
                "requirements": [
                    {{
                        "type": "functional|non-functional",
                        "description": "<REQUIRED: clear summary of what the stakeholder needs>",
                        "needs_clarification": false,
                        "evidence_quote": "<short exact phrase from the statement>"
                    }}
                ]
            }}

            NOTE: Only add "questions" key when needs_clarification is true:
            {{
                "type": "functional|non-functional",
                "description": "<REQUIRED>",
                "needs_clarification": true,
                "questions": ["<specific clarification question>"],
                "evidence_quote": "<short exact phrase from the statement>"
            }}

            If none found: {{ "requirements": [] }}

            REMINDER: Output ONLY the JSON object. No explanations, no preamble, no markdown fences.\n

            Stakeholder statement:
            \"\"\"{message}\"\"\"
        """.strip()
    
    def requirement_correction(self, message, existing_requirements=None, 
                               corrections=None, missed_items=None):
        existing_context = ""
        if existing_requirements and len(existing_requirements) > 0:
            existing_context = (
                "ALREADY SAVED REQUIREMENTS (do NOT re-include any of these - they are already persisted):\n"
                f"{existing_requirements}\n\n"
            )

        corrections_context = ""
        if corrections:
            corrections_context = (
                "Corrections to apply to the current extraction:\n"
                f"{corrections}\n\n"
            )

        missed_context = ""
        if missed_items:
            missed_context = (
                "Missed items to add as new requirements:\n"
                f"{missed_items}\n\n"
            )

        return f"""
            You are a Requirements Extraction Specialist performing a correction pass.

            {existing_context}{corrections_context}{missed_context}HARD RULES:
            1) Return ONLY requirements extracted from the CURRENT stakeholder statement below.
            2) Do NOT re-include any requirement from the ALREADY SAVED list above - those
            are already persisted and re-including them will create duplicates.
            3) Apply all corrections listed above to the relevant items in the current extraction.
            4) Add all missed items listed above as new requirements.
            5) If a correction references a req_id from a previous turn (not the current 
            extraction), skip it - it belongs to saved state, not to this pass.
            6) "description" MUST contain a clear summary. Never empty.
            7) "evidence_quote" MUST be a SHORT phrase (under 50 words) copied exactly 
            from the CURRENT statement below.

            OUTPUT ONLY THIS EXACT JSON STRUCTURE - NO OTHER TEXT:
            {{
                "requirements": [
                    {{
                        "type": "functional|non-functional",
                        "description": "<clear summary>",
                        "needs_clarification": false,
                        "evidence_quote": "<short exact phrase from current statement>"
                    }}
                ]
            }}

            If there is nothing new to add or correct: {{ "requirements": [] }}

            The response MUST start with {{ and end with }}.
            Do NOT re-output requirements from previous turns.

            Stakeholder statement:
            \"\"\"{message}\"\"\"
        """.strip()


    def issue_extraction(self, message, existing_requirements=None, existing_issues=None):
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

            {req_context}{issues_context}Extract issues ONLY if explicitly indicated
            by the stakeholder statement. Do NOT add generic risks unless mentioned.

            HARD RULES:
            1) Extract ONLY from stakeholder statements.
            2) "description" MUST clearly describe the issue. Never empty.
            3) "evidence_quote" MUST be a SHORT phrase (under 50 words) copied exactly from the statement.
            4) Do NOT re-extract issues that already exist above.
            5) If the statement contains NO new issues, return: {{ "issues": [] }}
            6) Extract a "process_gap" issue ONLY when a stakeholder describes a problem
            that exists RIGHT NOW in their current workflow - something broken, painful,
            or failing today, before any new system is built.
            Ask yourself: "Would this problem exist even if the new system is never built?"
            If YES → it is a process_gap. If NO → it is a missing feature, not an issue.

            Examples that DO qualify as process_gap:
            - "employees consistently book larger rooms for small meetings" → waste happening today
            - "no-shows are common, rooms get booked and never used" → recurring operational problem
            - "last-minute cancellations leave rooms empty" → current workflow failure
            - "I have no visibility into room utilisation" → current information gap

            Examples that DO NOT qualify (these are missing features, already in requirements):
            - "it would be useful to filter by floor" → desired feature, not a current problem
            - "there is no option for collaboration spaces" → missing feature
            - "this will help us find rooms conveniently" → justification sentence, not a problem
            - "having a way to indicate meeting type would be beneficial" → feature request

            7) Extract a "conflict" issue ONLY when two different stakeholders in this
            conversation have expressed directly contradictory needs about the SAME feature.
            A conflict requires evidence from TWO different agents - one wanting X and
            another explicitly wanting something incompatible with X.
            If only one stakeholder has spoken about a feature, do NOT extract a conflict.
            If a single stakeholder contradicts themselves within one statement 
            (e.g. wanting control but also open access), classify this as an 
            "ambiguity" - NOT a "conflict".

            8) Before extracting ANY process_gap, check the existing requirements 
            list above. If a requirement already exists describing the same need, 
            do NOT extract it as a process_gap - even if you can reframe it as 
            "the current system does not have X." Negating a requirement is not 
            evidence of a current operational problem. The evidence for a 
            process_gap must come from explicit stakeholder language describing 
            pain, failure, or frustration - not from the absence of a desired 
            feature.
            
            Red flag phrases that indicate misclassification:
            - "The current system does not provide..."
            - "There is no current way to..."
            - "The system lacks..."
            These are feature absence statements, not process gaps, unless the 
            stakeholder explicitly describes the resulting operational pain 
            (e.g. "because of this, meetings are missed", "this causes us to 
            lose bookings", "staff waste an hour each week on this").

            9) "related_requirement_id" MUST always be populated with the req_id
            of the most closely related requirement from the list above.
            - MUST BE AN INTEGER req_id from the existing requirements list.
            - Read the existing requirements list carefully before extracting.
            - Choose the requirement whose description is most topically related
                to this issue, even if the match is not perfect.
            - If the issue is entirely new with no related requirement yet,
                use the string "none" - never null, never blank.
            - NEVER leave related_requirement_id empty.

            OUTPUT ONLY VALID JSON WITH THIS EXACT STRUCTURE AND NO OTHER TEXT:
            {{
                "issues": [
                    {{
                        "type": "conflict|ambiguity|risk|blocker|concern|process_gap",
                        "description": "<REQUIRED: clear description of the issue>",
                        "severity": "high|medium|low",
                        "status": "open",
                        "related_requirement_id": "<REQUIRED: req_id>",
                        "evidence_quote": "<short exact phrase from the statement>"
                    }}
                ]
            }}

            If none found: {{ "issues": [] }}

            REMINDER: Output ONLY the JSON object. No explanations, no markdown.\n

            Stakeholder statement:
            \"\"\"{message}\"\"\"
        """.strip()
    
    def issue_correction(self, message, existing_requirements=None,
                         existing_issues=None, corrections=None, missed_items=None):
        req_context = ""
        if existing_requirements:
            req_context = f"Existing Requirements for Reference:\n{existing_requirements}\n\n"

        issues_context = ""
        if existing_issues and len(existing_issues) > 0:
            issues_context = (
                "ALREADY SAVED ISSUES (do NOT re-include any of these):\n"
                f"{existing_issues}\n\n"
            )

        corrections_context = ""
        if corrections:
            corrections_context = (
                "Corrections to apply to existing extractions:\n"
                f"{corrections}\n\n"
            )

        missed_context = ""
        if missed_items:
            missed_context = (
                "Missed items that must be added:\n"
                f"{missed_items}\n\n"
            )

        return f"""
            You are an Issues Detection Specialist performing a correction pass.

            {req_context}{issues_context}{corrections_context}{missed_context}HARD RULES:
            1) Apply all corrections listed above to existing issues.
            2) Add all missed items listed above as new issues.
            3) Do NOT re-extract issues that already exist and are not being corrected.
            4) "description" MUST clearly describe the issue. Never empty.
            5) "evidence_quote" MUST be a SHORT phrase (under 50 words) copied exactly from the statement.
            6) "related_requirement_id" in every output issue MUST be an integer 
            req_id from the existing requirements list above - never null, 
            never blank. If a missed item arrives without a related_requirement_id, 
            look up the most topically related requirement from the list yourself.

            OUTPUT ONLY VALID JSON WITH THIS EXACT STRUCTURE AND NO OTHER TEXT:
            {{
                "issues": [
                    {{
                        "type": "conflict|ambiguity|risk|blocker|concern|process_gap",
                        "description": "<clear description>",
                        "severity": "high|medium|low",
                        "status": "open",
                        "related_requirement_id": "<req_id>",
                        "evidence_quote": "<short exact phrase from the statement>"
                    }}
                ]
            }}

            If none found: {{ "issues": [] }}

            REMINDER: Output ONLY the JSON object. No explanations, no preamble, no markdown fences.

            Stakeholder statement:
            \"\"\"{message}\"\"\"
        """.strip()