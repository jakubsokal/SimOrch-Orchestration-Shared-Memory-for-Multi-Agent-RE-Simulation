from .base_agent import BaseAgent

class UserAgent(BaseAgent):
    def speak(self, message, role):
        if message is None:
            prompt = (
                "You are a stakeholder. Greet the Requirements Engineer."
            )
        elif role == "RE":
            prompt = (
                f"You are a stakeholder with simple needs. "
                f"The RE asked: '{message}'. "
                "Respond with what you would want from the system."
            )
        else:
            prompt = (
                f"You are a stakeholder. "
                f"The previous stakeholder said: '{message}'. "
                "Respond appropriately, consider their perspective and correct any ambiguities."
            )

        print(f"[UserAgent Prompt]: {prompt}")
        reply = self.agent.invoke(prompt)

        return reply