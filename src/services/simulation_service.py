import random
import datetime
import time
from ..orchestrator import Orchestrator
from ..agents import AgentFactory
from ..memory import SharedMemory
from ..logs import Logger
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

def run_simulation(config: dict):
    timestamp = datetime.datetime.now().isoformat()
    start_time = time.time()
    logger = Logger(scenario_id=config.get("scenario", {}).get("id", None))

    status = "completed"
    error = None
    seed = None
    turn_counter = 1

    print(f"[Simulation] Starting at {timestamp} with config: {config.get('scenario', {}).get('scenario_name', '')}")
    seed = config.get("scenario", {}).get("seed")
    random.seed(seed)

    api_key = os.getenv('OPEN_AI_KEY')
    description = config.get("scenario", {}).get("description", "")
    agents = build_agent_configs(config)
    max_turns = config.get("scenario", {}).get("max_turns", 10)
    scenarioTruths = config.get("scenarioTruths", None)

    try:
        re_agents = {}
        user_agents = {}
        for agent_config in agents:
            effective_api_key = agent_config.get('api_key') or api_key
            agent_cfg = {**agent_config, 'api_key': effective_api_key}
            agent = AgentFactory.create_agent(agent_cfg, description, seed=seed, scenarioTruths=scenarioTruths)
            
            if agent.role == 1:
                re_agents[agent.name] = agent
            elif agent.role == 2:
                user_agents[agent.name] = agent
            
            print(f"[LLM Factory] Created agent: {agent.name} Role: ({agent.role})")

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
            logger=logger,
        )

        type = config.get("scenario", {}).get("conversation_type", "dynamic")
        orchestrator.start(type)
        turn_counter = orchestrator.turn_counter

        logger.store_yaml(config)
    except Exception as e:
        status = "failed"
        error = e
        print(f"[Simulation] Failed: {e}")
        try:
            logger.store_yaml(config)
        except Exception:
            pass
        raise
    finally:
        end_time = time.time()
        elapsed_time = str(datetime.timedelta(seconds=round(end_time - start_time)))
        logger.store_run_details(
            timestamp,
            turn_counter,
            elapsed_time,
            seed=seed,
            successful=(status != "failed"),
            status=status,
            error=error,
        )


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
        re.pop("api_key", None)
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
                "communication_style": user.get('communication_style', 'cooperative'),
                "clarity_level": user.get('clarity_level', 'clear'),
                "domain_knowledge": user.get('domain_knowledge_level', 'high'),
                "revelation_strategy": user.get('revelation_strategy', 'proactive'),
                "revelation_rate": user.get('revelation_rate', 'medium'),
            },
            "context_prompt": user.get("context_prompt", ""),
            "api_key": user.get("api_key", ""),
        })
        user.pop("api_key", None)

    return agents