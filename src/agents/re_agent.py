from .base_agent import BaseAgent
from .persona_builder import PersonaBuilder

class REAgent(BaseAgent):
    def speak(self, message=None, role=None, conversation_history=None, analyst_output=None):
        system_context = f"{self.context_prompt}\n\nProject: {self.description}\n\n"

        print(f"[REAgent] Generating prompt with context: {self.persona}")

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
        if analyst_output:
            analyst_context = f"""
                Analyst findings in JSON format:
                {analyst_output}

                - Focus on requirements where needs_clarification=true
                - Follow up on open issues
                - Confirm unconfirmed requirements
                - Do NOT re-ask about confirmed requirements
            """

        if message is None:
            prompt = f"""
                {base_rules}

                {analyst_context}

                Start the interview by asking the stakeholder to describe what they need from the system.
                Keep your opening question open-ended and non-leading.
                """
        elif role == 1:
            prompt = f"""
                {base_rules}

                {history_context}
                {analyst_context}

                The stakeholder just said:
                "{message}"

                Ask ONE focused follow-up question targeting the most critical unresolved requirement or open issue.
                If all requirements are confirmed and no issues are open, respond with exactly: ELICITATION_COMPLETE
            """
        elif role == 2:
            prompt = f"""
                {base_rules}

                {history_context}
                {analyst_context}

                Another stakeholder just said:
                "{message}"

                Ask ONE focused question to clarify or expand on what was just said.
            """
        elif role == 3:
            prompt = f"""
                {base_rules}

                {history_context}
                {analyst_context}

                The analyst has just updated the requirements and issues.
                Based on the analyst's findings, ask ONE focused question targeting either the most critical unresolved requirement or highest severity open issue.
                If everything is confirmed and resolved, respond with exactly: ELICITATION_COMPLETE
            """
        else:
            return None

        final_prompt = system_context + prompt.strip()
        print(f"[REAgent]: Generating next question...")

        response = self.agent.invoke(final_prompt)

        if response and response.content:
            response = response.content.strip()
        
        print(f"[REAgent] Response: {response}")

        return response