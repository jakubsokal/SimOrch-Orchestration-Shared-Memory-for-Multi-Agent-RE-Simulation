from langchain_ollama import OllamaLLM

class BaseAgent:
    def __init__(self, name, role="agent", model_name="llama2", tools=None):
        self.name = name
        self.role = role
        self.agent = OllamaLLM(
            model=model_name,
            temperature=0.8,  # Increased for more varied responses
            num_predict=150,  # Limit response length
        )
    
    def speak(self, message, role):
        raise NotImplementedError  # MUST be overridden by subclasses