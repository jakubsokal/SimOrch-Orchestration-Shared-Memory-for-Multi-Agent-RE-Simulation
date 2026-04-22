from .base_agent import BaseAgent
from .persona_builder import PersonaBuilder

class UserAgent(BaseAgent):
    def speak(self, message=None, role=None, conversation_history=None):
        system_context = f"{self.context_prompt}\n\nProject: {self.description}\n\n"

        scenario_truths_formatted = self.get_scenario_truths_formatted()
        print(f"[UserAgent] Generating prompt... \n\n {conversation_history}\n\n")

        persona_context = PersonaBuilder.build_persona(self.persona, self.role)
        
        history_context = ""
        if conversation_history:
            history_context = f"""
                Previous conversation so far:
                    {conversation_history}

                Stay consistent with what you have already said. Do not contradict yourself.
            """

        base_rules = f"""You are {self.name}.
                    Respond in first person.
                    Do not include any other speakers in your response.
                    Do NOT use emotes, actions, or asterisks (e.g. *laughs*, *sighs*).
                    Do NOT use stage directions or describe physical actions.
                    Respond with dialogue only as if speaking in a real interview.
                    
                    Keep your response under {self.max_words} words.
                    
                    {persona_context}
                    
                    These are the truths about the scenario that you know and can reveal to the RE as needed:
                    {scenario_truths_formatted}
                    
                    Please response in first person as if you are the stakeholder responding to the RE's questions.
                """

        if message is None:
            prompt = f"""
                {base_rules}

                Greet the Requirements Engineer and give an overview of your role and what you need from the system.
                Be natural and conversational. Do not list everything at once - leave room for follow-up questions.

                {history_context}
            """
        elif role == 1:
            prompt = f"""
                {base_rules}

                The Requirements Engineer asked:
                \"\"\"{message}\"\"\"

                {history_context}

                Respond naturally as your character would. You may:
                - Answer directly if you know what you want
                - Express uncertainty if something is unclear to you
                - Raise concerns or frustrations relevant to your role
                - Avoid technical jargon unless it fits your persona
            """
        elif role == 2:
            prompt = f"""
                {base_rules}

                Another stakeholder said:
                \"\"\"{message}\"\"\"

                {history_context}

                Respond from your perspective. You may agree, disagree, or add nuance based on your role and priorities.
            """
        else:
            return None

        final_prompt = system_context + prompt.strip()
        print(f"[UserAgent]: Generating response...")

        response = self.agent.invoke(final_prompt)

        response_text = self.get_response(response)
        if response_text is not None:
            response_text = str(response_text).strip()

        print(f"[UserAgent] Response: {response_text}")

        return response_text