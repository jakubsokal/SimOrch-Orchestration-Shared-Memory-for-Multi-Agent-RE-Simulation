class BaseAgent:
    def __init__(self, name, llm, role="agent", context_prompt="", description="", max_words=512, persona=None, scenario_truths=None):
        self.name = name
        self.role = role
        self.agent = llm
        self.context_prompt = context_prompt
        self.description = description
        self.max_words = max_words
        self.persona = persona
        self.scenario_truths = scenario_truths

    def speak(self, message, role):
        raise NotImplementedError  # MUST be overridden by subclasses