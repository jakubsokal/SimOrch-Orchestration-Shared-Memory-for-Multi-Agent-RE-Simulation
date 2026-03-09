from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

LLM_TYPE = {
    "OLLAMA": OllamaLLM,
    "OPENAI": ChatOpenAI,
    # Future LLM integrations can be added here
}