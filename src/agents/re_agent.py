from agents.base_agent import BaseAgent

class REAgent(BaseAgent):

    def speak(self, message, role):
        if message is None:
            prompt = (
                "You are a Requirements Engineer. "
                "Start the interview by asking the stakeholder "
                "to describe what they need from the system."
            )
        elif role == "stakeholder":
            prompt = (
                f"You are a Requirements Engineer. The stakeholder said:\n\n"
                f"'{message}'\n\n"
                "Ask a clear follow-up question to get more requirements."
            )
        else:
            prompt = (
                f"You are a Requirements Engineer. The previous RE message was:\n\n"
                f"'{message}'\n\n"
                "Based on this, ask a relevant question to clarify or expand the requirements."
            )
        
        print(f"[REAgent Prompt]: {prompt}")
        reply = self.agent.invoke(prompt)
        
        return reply
