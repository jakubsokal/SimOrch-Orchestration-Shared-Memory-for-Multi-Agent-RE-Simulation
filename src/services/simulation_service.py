import random
import datetime
import time
from ..orchestrator import Orchestrator
from ..agents import AgentFactory
from ..memory import SharedMemory
from ..logs import Logger
from dotenv import load_dotenv
import os

load_dotenv()

def run_simulation(config: dict):
    timestamp = datetime.datetime.now().isoformat()
    start_time = time.time()
    print(f"[Simulation] Starting at {timestamp} with config: {config}")
    seed = config.get("runConfig", {}).get("seed", 42)
    random.seed(seed)

    api_key = os.getenv('OPEN_AI_KEY')
    description = config.get("scenario", {}).get("description", "")
    agents = build_agent_configs(config)
    max_turns = config.get("scenario", {}).get("max_turns", 10)
    scenarioTruths = config.get("scenario", {}).get("scenarioTruths", [])


    re_agents = {}
    user_agents = {}
    for agent_config in agents:
        agent = AgentFactory.create_agent(agent_config, description, seed=seed, scenarioTruths=scenarioTruths)
        if agent.role == 1:
            re_agents[agent.name] = agent
        elif agent.role == 2:
            user_agents[agent.name] = agent

    helper_agent = AgentFactory.create_agent({
        "name": "Analyst Agent",
        "role": 3,
        "model": "gpt-4o-mini",
        "provider": "OPENAI",
        "params": { 
            "temperature": 0,
            "top_p": 1.0,
        },
        "context_prompt": "",
        "api_key": api_key,
    }, description, seed=seed)

    orchestrator = Orchestrator(
        re_agents=re_agents,
        user_agents=user_agents,
        helper_agent=helper_agent,
        max_turns=max_turns,
        shared_memory=SharedMemory(),
        logger=Logger(),
    )
    type = config.get("scenario", {}).get("conversation_type", "dynamic")
    print(agents)
    orchestrator.start(type)
    orchestrator.logger.store_yaml(config)

    end_time = time.time()
    elapsed_time = str(datetime.timedelta(seconds=round(end_time - start_time)))
    orchestrator.logger.store_run_details(timestamp, orchestrator.turn_counter, elapsed_time, seed=seed)


def build_agent_configs(config: dict) -> list:
    agents = []
    for re in config.get("re_agents", []):
        agents.append({
            "name": re.get("name"),
            "role": 1,
            "model": re.get("model"),
            "provider": re.get("provider", "OLLAMA").upper(),
            "params": {
                    "temperature": re.get("temperature", 0.0),
                    "top_p": re.get("top_p", 1.0),
                    "max_tokens": re.get("max_tokens", 512),
            },
            "persona": {   
                "domain_knowledge": re.get("domain_knowledge", ""),
                "revelation_strategy": re.get("revelation_strategy", ""),
                "communication_style": re.get("communication_strategy", ""),
                "clarity_level": re.get("clarity_level", ""),
                "revelation_rate": re.get("revelation_rate", ""),
            },
            "api_key": re.get("api_key", ""),
            "context_prompt": re.get("context_prompt", ""),
        })
    for user in config.get("user_agents", []):
        agents.append({
            "name": user.get("name"),
            "role": 2,
            "model": user.get("model"),
            "provider": user.get("provider", "OLLAMA").upper(),
            "params": {
                    "temperature": user.get("temperature", 0.0),
                    "top_p": user.get("top_p", 1.0),
                    "max_tokens": user.get("max_tokens", 512),
                },
            "persona": {
                "communication_style": user.get('communication_style', 'default'),
                "clarity_level": user.get('clarity_level', 'medium'),
                "domain_knowledge": user.get('domain_knowledge_level', 'medium'),
                "revelation_strategy": user.get('revelation_strategy', 'gradual'),
                "revelation_rate": user.get('revelation_rate', 'medium'),
            },
            "context_prompt": user.get("context_prompt", ""),
            "api_key": user.get("api_key", ""),
        })
    return agents