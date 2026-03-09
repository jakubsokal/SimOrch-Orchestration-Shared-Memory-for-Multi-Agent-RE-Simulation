
from .llm_enum import LLM_TYPE
import os
from dotenv import load_dotenv 

load_dotenv()

PROVIDER_TOKEN_PARAM = {
    "OLLAMA": "num_predict",
    "OPENAI": "max_tokens",
    "GEMINI": "max_output_tokens",
    "GROK": "max_tokens",
    "ANTHROPIC": "max_tokens"
}

def get_model_params(provider, params):
    params = params.copy()
    token_limit = params.pop("num_predict", None)
    if token_limit:
        param_name = PROVIDER_TOKEN_PARAM.get(provider.upper(), "max_tokens")
        params[param_name] = token_limit
    return params

class LLMFactory:
    def create_llm(llm_cfg, seed):
        api_key = os.getenv('OPEN_AI_KEY')
        print(f"[LLMFactory] Creating LLM with config: {llm_cfg['provider']}, {llm_cfg['model']}")
        
        provider = llm_cfg['provider'].upper()
        model = llm_cfg['model']
        params = get_model_params(provider, llm_cfg.get('params', {}))

        if not provider or not model:
            raise ValueError("LLM configuration needs a provider and a model.")
        
        llm_class = LLM_TYPE.get(provider)
        
        if not llm_class:
            raise ValueError(f"LLM '{provider}' is not supported.")
        
        return llm_class(model=model, seed=seed, **params, api_key=llm_cfg.get('api_key', api_key))