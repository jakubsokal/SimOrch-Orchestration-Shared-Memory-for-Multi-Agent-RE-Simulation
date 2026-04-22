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

    @staticmethod
    def get_response(response):
        if response is None:
            return None

        if isinstance(response, str):
            return response

        content = getattr(response, "content", None)
        if content is not None:
            return content

        return str(response)

    def get_scenario_truths_formatted(self, max_chars_per_statement: int = 240) -> str:
        if not self.scenario_truths:
            return ""

        if isinstance(self.scenario_truths, str):
            return self.scenario_truths

        if not isinstance(self.scenario_truths, list):
            # Best-effort fallback
            return str(self.scenario_truths)

        lines = []
        for truth in self.scenario_truths:
            if not isinstance(truth, dict):
                lines.append(f"  {str(truth)}")
                continue

            truth_id = truth.get("id", "?")
            truth_type = truth.get("type", "")
            statement = truth.get("statement", "")

            statement = " ".join(str(statement).split())
            if max_chars_per_statement and len(statement) > max_chars_per_statement:
                statement = statement[:max_chars_per_statement].rstrip() + "…"

            prefix = f"  [{truth_id}]"
            if truth_type:
                prefix += f" ({truth_type})"
            lines.append(f"{prefix} {statement}")

        return "\n".join(lines)

    def speak(self, message, role):
        raise NotImplementedError  # MUST be overridden by subclasses