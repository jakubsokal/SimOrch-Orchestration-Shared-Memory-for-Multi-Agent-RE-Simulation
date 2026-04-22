from .base_agent import BaseAgent
from .persona_builder import PersonaBuilder
from .agent_types import AgentRole

class REAgent(BaseAgent):
    def speak(self, message=None, role=None, conversation_history=None, 
              saved_context=None, current_extraction=None, saved_extractions=None, extraction_type=None):
        system_context = f"{self.context_prompt}\n\nProject: {self.description}\n\n"

        print(f"[REAgent] Generating prompt...")

        persona_context = PersonaBuilder.build_persona(self.persona, self.role)

        base_rules = (
            f"""You are a Requirements Engineer conducting a stakeholder interview. "
                Ask only ONE question per turn. 
                Do not invent or assume details. 
                Keep questions clear and jargon-free for the stakeholder.

                Keep your response under {self.max_words} words.\n
                
                {persona_context}

                Please reply in first person as if you are the RE asking the question.            
            """
        )

        history_context = ""
        if conversation_history:
            history_context = f"""
                Conversation so far in JSON format:
                {conversation_history}
                Stay consistent with what has already been said. Do not contradict yourself.
            """

        analyst_context = ""
        if saved_context:
            if isinstance(saved_context, list):
                unresolved = sorted(
                    [r for r in saved_context
                    if r.get("requirement", {}).get("needs_clarification", False)],
                    key=lambda r: r.get("req_id", 999)
                )
                next_to_clarify = unresolved[0] if unresolved else None
            else:
                next_to_clarify = None
            
            analyst_context = f"""
                Analyst findings:
                {saved_context}

                Priority rules when using analyst findings:
                - Only act on needs_clarification=true items that belong to your
                CURRENT questioning category
                - Within that category, address the item with the LOWEST req_id first.
                Next item to clarify: {next_to_clarify}
                - Do NOT follow tangents introduced by 'One thing worth mentioning is...'
                unless they fall within your current questioning category
                - If an item belongs to a later category, note it and return to it
                when you reach that category
                - If all items are confirmed and no issues are open, respond with
                exactly: STOP_SIMULATION
            """

        if message is None:
            prompt = f"""
                {base_rules}

                {analyst_context}

                Start the interview by asking the stakeholder to describe what they need from the system.
                Keep your opening question open-ended and non-leading.
                """
        elif role == AgentRole.RE_AGENT:
            prompt = f"""
                {base_rules}

                {history_context}
                {analyst_context}

                The requirement engineer just said:
                "{message}"

                Ask ONE focused follow-up question targeting the most critical unresolved requirement or open issue.
                If all requirements are confirmed and no issues are open, respond with exactly: ELICITATION_COMPLETE
            """
        elif role == AgentRole.USER_AGENT:
            prompt = f"""
                {base_rules}

                {history_context}
                {analyst_context}

                A stakeholder just said:
                "{message}"

                Ask ONE focused follow-up question targeting the most critical
                unresolved requirement or open issue based on the priority rules above.
                If all requirements are confirmed and no issues are open, respond
                with exactly: ELICITATION_COMPLETE
            """
        elif role == AgentRole.VALIDATE:
            type_rule = (
                "Do NOT flag requirements as missed items. "
                "Only flag genuine issues: conflicts, ambiguities, risks, "
                "blockers, concerns, or process gaps explicitly stated in the message. "
                "If the stakeholder statement contains no such issues, return validated=true with empty lists. "
                "Requirements are NOT issues - do not reclassify them."
                if extraction_type == "ISSUE"
                else
                "Do NOT flag issues as missed items. "
                "Only flag requirements - things the system must do or qualities it must have."
            )

            already_saved = saved_extractions if saved_extractions else "[]"

            prompt = f"""
                You are validating a {extraction_type} extraction only.
                {type_rule}

                Most recent stakeholder statement:
                \"\"\"{message}\"\"\"

                ALREADY SAVED ITEMS (do not re-flag these):
                The following {extraction_type}s have already been captured in previous turns.
                You MUST treat this list as an exclusion list.
                If an item from this list appears in the current statement, it is NOT a missed item - it is already saved.
                Do NOT include any of these in missed_items under any circumstances:
                {already_saved}

                Before flagging ANY missed_item, check BOTH:
                1. Is it absent from the current extraction?
                2. Is it also absent from the ALREADY SAVED ITEMS above?
                If it exists in EITHER place - even worded differently - do NOT flag it.

                Analyst extracted the following from ONLY the CURRENT statement above (JSON):
                {current_extraction  if current_extraction  else "{}"}

                Your job: validate whether the analyst's extraction accurately reflects
                what was said in the CURRENT statement only.

                CRITICAL RULES:
                - "validated" MUST be false if corrections or missed_items are non-empty.
                - "validated" can only be true if BOTH lists are completely empty.
                - Only flag an item in missed_items if ALL of these are true:
                    1. It appears in the CURRENT statement
                    2. It is NOT in the ALREADY SAVED ITEMS list above
                    3. It is NOT present in the analyst's current extraction
                - Do NOT invent items that were not stated in the current message.
                - A requirement is only wrong if it misrepresents the evidence quote,
                not just because the wording differs slightly.
                - CONSISTENCY RULE: If both "corrections" and "missed_items" are empty,
                "validated" MUST be true. Returning validated=false with two empty 
                lists is a contradiction and is not permitted.
                - SEMANTIC EQUIVALENCE RULE: Before flagging a missed_item, check whether 
                the current extraction already contains a requirement with the same 
                meaning, even if worded differently. Ask yourself: "Does any existing 
                extracted requirement cover this capability, even partially?" 
                If YES - do NOT flag it as missed. Paraphrasing is not a miss.
                Only flag something as genuinely absent if NO extracted requirement 
                covers that capability at all.

                Respond with ONLY a valid JSON object - no preamble, no markdown:
                {{
                    "validated": true,
                    "corrections": [
                        {{
                            "req_id": 1,
                            "issue": "<what is wrong>",
                            "suggested_fix": "<corrected description>"
                        }}
                    ],
                    "missed_items": [
                        {{
                            "item_type": "functional|non-functional",
                            "description": "<what was missed>",
                            "evidence_quote": "<exact short phrase from the CURRENT statement>"
                        }}
                    ]
                }}

                If everything is correct return:
                {{"validated": true, "corrections": [], "missed_items": []}}

                NOTE: The extraction specialist merges related aspects of the same 
                capability into a single requirement. A requirement like "filter by 
                date range, room, severity, and person" covers all four filter 
                criteria - do NOT flag individual criteria as missed items if they 
                are already described within an existing requirement's description. 
                Only flag something as missed if it represents an entirely distinct 
                system capability with no coverage in any existing requirement.

                Start your response with {{ and end with }}.
            """
        else:
            return None

        final_prompt = system_context + prompt.strip()

        response = self.agent.invoke(final_prompt)

        response_text = self.get_response(response)
        if response_text is not None:
            response_text = str(response_text).strip()

        print(f"[REAgent] Response: {response_text}")

        return response_text